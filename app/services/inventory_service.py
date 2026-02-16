from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock

from app.models import LowStockItem, Product, ProductCreate


class InventoryService:
    def __init__(self) -> None:
        self._products: dict[str, Product] = {}
        self._lock = RLock()

    def list_products(self) -> list[Product]:
        with self._lock:
            return sorted(self._products.values(), key=lambda p: p.sku)

    def get_product(self, sku: str) -> Product | None:
        with self._lock:
            return self._products.get(sku)

    def upsert_product(self, data: ProductCreate) -> Product:
        now = datetime.now(UTC)
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
                updated_at=datetime.now(UTC),
            )
            self._products[sku] = updated
            return updated

    def bulk_upsert(self, records: list[ProductCreate]) -> int:
        count = 0
        for record in records:
            self.upsert_product(record)
            count += 1
        return count

    def low_stock(self, threshold: int) -> list[LowStockItem]:
        with self._lock:
            return [
                LowStockItem(sku=p.sku, name=p.name, quantity=p.quantity)
                for p in sorted(self._products.values(), key=lambda p: p.quantity)
                if p.quantity <= threshold
            ]
