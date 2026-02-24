import pytest

pytest.importorskip('sqlalchemy')

pytest.importorskip('httpx')

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)
API_KEY = get_settings().api_key.get_secret_value()


@pytest.fixture(autouse=True)
def clear_service_state() -> None:
    app.state.inventory_service.reset()


def test_health_check() -> None:
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_create_list_and_adjust_product() -> None:
    create = client.post(
        '/products',
        headers={'x-api-key': API_KEY},
        json={'sku': 'SKU-1', 'name': 'Widget', 'price': '9.99', 'quantity': 20},
    )
    assert create.status_code == 200
    assert create.json()['sku'] == 'SKU-1'
    assert create.headers['x-request-id']

    listing = client.get('/products', params={'limit': 10, 'offset': 0})
    assert listing.status_code == 200
    payload = listing.json()
    assert payload['total'] == 1
    assert payload['limit'] == 10
    assert payload['offset'] == 0
    assert any(p['sku'] == 'SKU-1' for p in payload['items'])

    adjust = client.post(
        '/products/SKU-1/adjust',
        headers={'x-api-key': API_KEY},
        json={'delta': -5},
    )
    assert adjust.status_code == 200
    assert adjust.json()['quantity'] == 15


def test_auth_rejected_without_api_key() -> None:
    response = client.post(
        '/products',
        json={'sku': 'SKU-2', 'name': 'Denied', 'price': '5.00', 'quantity': 1},
    )
    assert response.status_code == 401


def test_prevent_negative_inventory() -> None:
    client.post(
        '/products',
        headers={'x-api-key': API_KEY},
        json={'sku': 'SKU-NEG', 'name': 'Limited', 'price': '10.00', 'quantity': 1},
    )

    response = client.post(
        '/products/SKU-NEG/adjust',
        headers={'x-api-key': API_KEY},
        json={'delta': -2},
    )
    assert response.status_code == 400
    assert 'cannot become negative' in response.json()['detail'].lower()


def test_inventory_sync_idempotency_and_low_stock_report() -> None:
    sync_1 = client.post(
        '/sync/inventory',
        headers={'x-api-key': API_KEY, 'x-idempotency-key': 'sync-key-001'},
        json={
            'source': 'marketplace-a',
            'records': [
                {'sku': 'SKU-A', 'name': 'A-Item', 'price': '1.20', 'quantity': 3},
                {'sku': 'SKU-B', 'name': 'B-Item', 'price': '2.20', 'quantity': 30},
            ],
        },
    )
    assert sync_1.status_code == 200

    sync_2 = client.post(
        '/sync/inventory',
        headers={'x-api-key': API_KEY, 'x-idempotency-key': 'sync-key-001'},
        json={
            'source': 'marketplace-a',
            'records': [
                {'sku': 'SKU-A', 'name': 'A-Item', 'price': '9.99', 'quantity': 999},
            ],
        },
    )
    assert sync_2.status_code == 200
    assert sync_2.json()['timestamp'] == sync_1.json()['timestamp']

    report = client.get('/reports/low-stock')
    assert report.status_code == 200
    skus = [r['sku'] for r in report.json()]
    assert 'SKU-A' in skus


def test_metrics_endpoint() -> None:
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'shopease_http_requests_total' in response.text
