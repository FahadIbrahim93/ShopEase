# ShopEase Architecture (Current MVP)

## Runtime
- Python FastAPI service (`app/main.py`)
- In-memory inventory service with thread-safe locking (`app/services/inventory_service.py`)

## API Boundaries
- Read endpoints: public (`/healthz`, `/metrics`, `/products`, `/reports/low-stock`)
- Write endpoints: protected by API key (`/products`, `/products/{sku}/adjust`, `/sync/inventory`)

## Security Controls
- API-key check for mutating operations.
- Input validation via Pydantic models.
- Negative inventory prevention.
- CI-integrated static security scanning (`bandit`).

## Observability
- Structured logs with request IDs.
- Prometheus metrics:
  - request count
  - request latency histogram

## Known Constraints
- Data is in-memory only (non-durable).
- No auth identity/roles beyond API key.
- No distributed tracing backend configured yet.

## Next Evolution
- Replace in-memory storage with PostgreSQL.
- Add Alembic migrations.
- Add idempotency keys for sync endpoint.
- Add OpenTelemetry exporters and alert rules.
