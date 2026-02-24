from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock

from app.models import InventorySyncResult, LowStockItem, Product, ProductCreate


class InventoryService:
    def __init__(self) -> None:
        self._products: dict[str, Product] = {}
        self._sync_cache: dict[str, InventorySyncResult] = {}
        self._lock = RLock()

    def reset(self) -> None:
        with self._lock:
            self._products.clear()
            self._sync_cache.clear()

    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        with self._lock:
            products = sorted(self._products.values(), key=lambda p: p.sku)
            total = len(products)
            return products[offset : offset + limit], total

    def get_product(self, sku: str) -> Product | None:
        with self._lock:
            return self._products.get(sku)

    def upsert_product(self, data: ProductCreate) -> Product:
        now = datetime.now(timezone.utc)
        product = Product(
            sku=data.sku,
            name=data.name,
            price=data.price,
            quantity=data.quantity,
            updated_at=now,
        )
        with self._lock:
            self._products[data.sku] = product
        return product

    def adjust_inventory(self, sku: str, delta: int) -> Product | None:
        with self._lock:
            existing = self._products.get(sku)
            if existing is None:
                return None
            new_qty = existing.quantity + delta
            if new_qty < 0:
                raise ValueError('Inventory cannot become negative')
            updated = Product(
                sku=existing.sku,
                name=existing.name,
                price=existing.price,
                quantity=new_qty,
                updated_at=datetime.now(timezone.utc),
            )
            self._products[sku] = updated
            return updated

    def sync_inventory(
        self,
        *,
        source: str,
        records: list[ProductCreate],
        idempotency_key: str | None,
    ) -> InventorySyncResult:
        with self._lock:
            if idempotency_key and idempotency_key in self._sync_cache:
                return self._sync_cache[idempotency_key]

            now = datetime.now(timezone.utc)
            for record in records:
                self._products[record.sku] = Product(
                    sku=record.sku,
                    name=record.name,
                    price=record.price,
                    quantity=record.quantity,
                    updated_at=now,
                )

            result = InventorySyncResult(source=source, upserted=len(records), timestamp=now)
            if idempotency_key:
                self._sync_cache[idempotency_key] = result
            return result

    def low_stock(self, threshold: int) -> list[LowStockItem]:
        with self._lock:
            return [
                LowStockItem(sku=p.sku, name=p.name, quantity=p.quantity)
                for p in sorted(self._products.values(), key=lambda p: p.quantity)
                if p.quantity <= threshold
            ]
