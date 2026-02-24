from decimal import Decimal

from app.models import ProductCreate
from app.services.inventory_service import InventoryService


def test_sync_inventory_idempotent_by_key() -> None:
    service = InventoryService()

    first = service.sync_inventory(
        source='market-a',
        records=[ProductCreate(sku='SKU-1', name='One', price=Decimal('2.00'), quantity=2)],
        idempotency_key='sync-key-1',
    )
    second = service.sync_inventory(
        source='market-a',
        records=[ProductCreate(sku='SKU-1', name='Changed', price=Decimal('3.00'), quantity=5)],
        idempotency_key='sync-key-1',
    )

    assert second.timestamp == first.timestamp
    assert second.upserted == first.upserted
    product = service.get_product('SKU-1')
    assert product is not None
    assert product.name == 'One'


def test_list_products_paginates_and_reports_total() -> None:
    service = InventoryService()
    service.upsert_product(ProductCreate(sku='AA', name='A1', price=Decimal('1.00'), quantity=3))
    service.upsert_product(ProductCreate(sku='BB', name='B1', price=Decimal('1.00'), quantity=1))
    service.upsert_product(ProductCreate(sku='CC', name='C1', price=Decimal('1.00'), quantity=2))

    items, total = service.list_products(limit=2, offset=1)

    assert total == 3
    assert [item.sku for item in items] == ['BB', 'CC']
