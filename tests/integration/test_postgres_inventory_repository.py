from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest

pytest.importorskip('sqlalchemy')

from app.models import ProductCreate
from app.repositories.postgres_inventory_repository import PostgresInventoryRepository
from app.services.inventory_service import InventoryService


@pytest.fixture(scope='module')
def postgres_service() -> InventoryService:
    database_url = os.getenv('TEST_DATABASE_URL')
    if not database_url:
        pytest.skip('TEST_DATABASE_URL is not configured')
    if 'postgresql' not in database_url:
        pytest.skip('TEST_DATABASE_URL must point to PostgreSQL')

    repository = PostgresInventoryRepository(database_url)
    repository.create_schema()
    repository.reset()
    return InventoryService(repository)


def test_restart_persistence(postgres_service: InventoryService) -> None:
    postgres_service.reset()
    postgres_service.upsert_product(
        ProductCreate(sku='PERSIST-1', name='Persisted Item', price=Decimal('12.00'), quantity=7)
    )

    database_url = os.environ['TEST_DATABASE_URL']
    restarted = InventoryService(PostgresInventoryRepository(database_url))

    product = restarted.get_product('PERSIST-1')
    assert product is not None
    assert product.quantity == 7


def test_concurrent_adjustments_are_correct(postgres_service: InventoryService) -> None:
    postgres_service.reset()
    postgres_service.upsert_product(
        ProductCreate(sku='CONC-1', name='Concurrent Item', price=Decimal('4.00'), quantity=0)
    )

    def increment() -> None:
        updated = postgres_service.adjust_inventory('CONC-1', 1)
        assert updated is not None

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(lambda _: increment(), range(100)))

    final = postgres_service.get_product('CONC-1')
    assert final is not None
    assert final.quantity == 100
