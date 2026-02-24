import hmac
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.config import Settings, get_settings
from app.models import (
    ErrorResponse,
    InventoryAdjustment,
    InventorySyncRequest,
    InventorySyncResult,
    LowStockItem,
    Product,
    ProductCreate,
    ProductListResponse,
)
from app.repositories.postgres_inventory_repository import PostgresInventoryRepository
from app.services.inventory_service import InventoryService

logger = logging.getLogger('shopease')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

REQUEST_COUNT = Counter(
    'shopease_http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status'],
)
REQUEST_LATENCY = Histogram(
    'shopease_http_request_latency_seconds',
    'Request latency',
    ['method', 'path'],
)

app = FastAPI(title='ShopEase API', version='0.3.0')
settings = get_settings()
repository = PostgresInventoryRepository(settings.database_url)
repository.create_schema()
app.state.inventory_service = InventoryService(repository)


def get_inventory_service(request: Request) -> InventoryService:
    return request.app.state.inventory_service


@app.middleware('http')
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get('x-request-id', str(uuid4()))
    start = perf_counter()
    try:
        response = await call_next(request)
    except Exception:  # noqa: BLE001
        logger.exception('Unhandled exception request_id=%s path=%s', request_id, request.url.path)
        response = JSONResponse(status_code=500, content={'detail': 'Internal server error'})

    elapsed = perf_counter() - start
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
    response.headers['x-request-id'] = request_id
    response.headers['x-process-time'] = str(elapsed)
    return response


def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    expected_key = settings.api_key.get_secret_value()
    if x_api_key is None or not hmac.compare_digest(x_api_key, expected_key):
        raise HTTPException(status_code=401, detail='Invalid API key')


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/metrics')
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get('/products', response_model=ProductListResponse)
def list_products(
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: InventoryService = Depends(get_inventory_service),
) -> ProductListResponse:
    items, total = service.list_products(limit=limit, offset=offset)
    return ProductListResponse(items=items, total=total, limit=limit, offset=offset)


@app.post(
    '/products',
    response_model=Product,
    responses={401: {'model': ErrorResponse}},
)
def create_or_update_product(
    payload: ProductCreate,
    _: None = Depends(require_api_key),
    service: InventoryService = Depends(get_inventory_service),
) -> Product:
    created = service.upsert_product(payload)
    logger.info('Product upserted sku=%s quantity=%s', created.sku, created.quantity)
    return created


@app.post(
    '/products/{sku}/adjust',
    response_model=Product,
    responses={400: {'model': ErrorResponse}, 404: {'model': ErrorResponse}},
)
def adjust_product_inventory(
    sku: str,
    payload: InventoryAdjustment,
    _: None = Depends(require_api_key),
    service: InventoryService = Depends(get_inventory_service),
) -> Product:
    try:
        updated = service.adjust_inventory(sku, payload.delta)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return updated


@app.get('/reports/low-stock', response_model=list[LowStockItem])
def get_low_stock_report(
    settings: Settings = Depends(get_settings),
    service: InventoryService = Depends(get_inventory_service),
) -> list[LowStockItem]:
    return service.low_stock(settings.low_stock_threshold)


@app.post(
    '/sync/inventory',
    response_model=InventorySyncResult,
    responses={400: {'model': ErrorResponse}, 401: {'model': ErrorResponse}},
)
def sync_inventory(
    payload: InventorySyncRequest,
    _: None = Depends(require_api_key),
    service: InventoryService = Depends(get_inventory_service),
    x_idempotency_key: str | None = Header(default=None),
) -> InventorySyncResult:
    if x_idempotency_key is not None and len(x_idempotency_key.strip()) < 8:
        raise HTTPException(
            status_code=400,
            detail='x-idempotency-key must be at least 8 characters',
        )

    result = service.sync_inventory(
        source=payload.source,
        records=payload.records,
        idempotency_key=x_idempotency_key,
    )
    logger.info('Inventory sync source=%s upserted=%s', result.source, result.upserted)
    return result
