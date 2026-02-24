from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from app.models import InventorySyncResult, LowStockItem, Product, ProductCreate
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository) -> None:
        self._repository = repository

    def reset(self) -> None:
        self._repository.reset()

    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        return self._repository.list_products(limit=limit, offset=offset)

    def get_product(self, sku: str) -> Product | None:
        return self._repository.get_product(sku)

    def upsert_product(self, data: ProductCreate) -> Product:
        return self._repository.upsert_product(data)

    def adjust_inventory(self, sku: str, delta: int) -> Product | None:
        return self._repository.adjust_inventory(sku, delta)

    def sync_inventory(
        self,
        *,
        source: str,
        records: list[ProductCreate],
        idempotency_key: str | None,
    ) -> InventorySyncResult:
        if idempotency_key:
            existing = self._repository.get_sync_result(idempotency_key)
            if existing:
                return existing

        now = datetime.now(timezone.utc)
        self._repository.upsert_many(records, timestamp=now)
        result = InventorySyncResult(source=source, upserted=len(records), timestamp=now)

        if idempotency_key:
            self._repository.record_sync_result(
                idempotency_key=idempotency_key,
                source=source,
                upserted=result.upserted,
                timestamp=result.timestamp,
                record_hash=self._hash_records(records),
            )
        return result

    def low_stock(self, threshold: int) -> list[LowStockItem]:
        return self._repository.low_stock(threshold)

    @staticmethod
    def _hash_records(records: list[ProductCreate]) -> str:
        normalized = [r.model_dump(mode='json') for r in records]
        payload = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()
