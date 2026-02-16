from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)
API_KEY = get_settings().api_key


def test_health_check() -> None:
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_create_list_and_adjust_product() -> None:
    create = client.post(
        '/products',
        headers={'x-api-key': API_KEY},
        json={'sku': 'SKU-1', 'name': 'Widget', 'price': 9.99, 'quantity': 20},
    )
    assert create.status_code == 200
    assert create.json()['sku'] == 'SKU-1'

    listing = client.get('/products')
    assert listing.status_code == 200
    assert any(p['sku'] == 'SKU-1' for p in listing.json())

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
        json={'sku': 'SKU-2', 'name': 'Denied', 'price': 5.0, 'quantity': 1},
    )
    assert response.status_code == 401


def test_prevent_negative_inventory() -> None:
    client.post(
        '/products',
        headers={'x-api-key': API_KEY},
        json={'sku': 'SKU-NEG', 'name': 'Limited', 'price': 10.0, 'quantity': 1},
    )

    response = client.post(
        '/products/SKU-NEG/adjust',
        headers={'x-api-key': API_KEY},
        json={'delta': -2},
    )
    assert response.status_code == 400
    assert 'cannot become negative' in response.json()['detail'].lower()


def test_inventory_sync_and_low_stock_report() -> None:
    sync = client.post(
        '/sync/inventory',
        headers={'x-api-key': API_KEY},
        json={
            'source': 'marketplace-a',
            'records': [
                {'sku': 'SKU-A', 'name': 'A', 'price': 1.2, 'quantity': 3},
                {'sku': 'SKU-B', 'name': 'B', 'price': 2.2, 'quantity': 30},
            ],
        },
    )
    assert sync.status_code == 200
    assert sync.json()['upserted'] == 2

    report = client.get('/reports/low-stock')
    assert report.status_code == 200
    skus = [r['sku'] for r in report.json()]
    assert 'SKU-A' in skus


def test_metrics_endpoint() -> None:
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'shopease_http_requests_total' in response.text
