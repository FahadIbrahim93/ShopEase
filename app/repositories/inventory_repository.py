from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.models import InventorySyncResult, LowStockItem, Product, ProductCreate


class InventoryRepository(ABC):
    @abstractmethod
    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]: ...

    @abstractmethod
    def get_product(self, sku: str) -> Product | None: ...

    @abstractmethod
    def upsert_product(self, data: ProductCreate) -> Product: ...

    @abstractmethod
    def upsert_many(self, records: list[ProductCreate], *, timestamp: datetime) -> None: ...

    @abstractmethod
    def adjust_inventory(self, sku: str, delta: int) -> Product | None: ...

    @abstractmethod
    def get_sync_result(self, idempotency_key: str) -> InventorySyncResult | None: ...

    @abstractmethod
    def record_sync_result(
        self,
        *,
        idempotency_key: str,
        source: str,
        upserted: int,
        timestamp: datetime,
        record_hash: str,
    ) -> InventorySyncResult: ...

    @abstractmethod
    def low_stock(self, threshold: int) -> list[LowStockItem]: ...

    @abstractmethod
    def reset(self) -> None: ...
