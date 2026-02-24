from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Select, create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import ProductRecord, SyncIdempotencyRecord
from app.models import InventorySyncResult, LowStockItem, Product, ProductCreate
from app.repositories.inventory_repository import InventoryRepository


class PostgresInventoryRepository(InventoryRepository):
    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, future=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self._engine)

    def list_products(self, *, limit: int, offset: int) -> tuple[list[Product], int]:
        with self._session_factory() as session:
            query: Select[tuple[ProductRecord]] = select(ProductRecord).order_by(ProductRecord.sku)
            items = session.execute(query.offset(offset).limit(limit)).scalars().all()
            total = session.scalar(select(func.count()).select_from(ProductRecord)) or 0
            return [self._to_product(record) for record in items], total

    def get_product(self, sku: str) -> Product | None:
        with self._session_factory() as session:
            record = session.get(ProductRecord, sku)
            return self._to_product(record) if record else None

    def upsert_product(self, data: ProductCreate) -> Product:
        with self._session_factory.begin() as session:
            record = session.get(ProductRecord, data.sku)
            now = datetime.now(timezone.utc)
            if record is None:
                record = ProductRecord(
                    sku=data.sku,
                    name=data.name,
                    price=data.price,
                    quantity=data.quantity,
                    updated_at=now,
                )
                session.add(record)
            else:
                record.name = data.name
                record.price = data.price
                record.quantity = data.quantity
                record.updated_at = now
            return self._to_product(record)

    def adjust_inventory(self, sku: str, delta: int) -> Product | None:
        with self._session_factory.begin() as session:
            record = session.get(ProductRecord, sku, with_for_update=True)
            if record is None:
                return None
            new_qty = record.quantity + delta
            if new_qty < 0:
                raise ValueError('Inventory cannot become negative')
            record.quantity = new_qty
            record.updated_at = datetime.now(timezone.utc)
            return self._to_product(record)

    def get_sync_result(self, idempotency_key: str) -> InventorySyncResult | None:
        with self._session_factory() as session:
            record = session.get(SyncIdempotencyRecord, idempotency_key)
            if record is None:
                return None
            return InventorySyncResult(
                source=record.source,
                upserted=record.upserted,
                timestamp=record.timestamp,
            )

    def record_sync_result(
        self,
        *,
        idempotency_key: str,
        source: str,
        upserted: int,
        timestamp: datetime,
        record_hash: str,
    ) -> InventorySyncResult:
        with self._session_factory.begin() as session:
            record = session.get(SyncIdempotencyRecord, idempotency_key, with_for_update=True)
            if record is None:
                record = SyncIdempotencyRecord(
                    idempotency_key=idempotency_key,
                    source=source,
                    upserted=upserted,
                    timestamp=timestamp,
                    record_hash=record_hash,
                )
                session.add(record)
            return InventorySyncResult(
                source=record.source,
                upserted=record.upserted,
                timestamp=record.timestamp,
            )

    def low_stock(self, threshold: int) -> list[LowStockItem]:
        with self._session_factory() as session:
            rows = session.execute(
                select(ProductRecord)
                .where(ProductRecord.quantity <= threshold)
                .order_by(ProductRecord.quantity)
            ).scalars()
            return [LowStockItem(sku=r.sku, name=r.name, quantity=r.quantity) for r in rows]

    def reset(self) -> None:
        with self._session_factory.begin() as session:
            session.query(SyncIdempotencyRecord).delete()
            session.query(ProductRecord).delete()

    def upsert_many(self, records: list[ProductCreate], *, timestamp: datetime) -> None:
        with self._session_factory.begin() as session:
            for data in records:
                record = session.get(ProductRecord, data.sku)
                if record is None:
                    session.add(
                        ProductRecord(
                            sku=data.sku,
                            name=data.name,
                            price=Decimal(data.price),
                            quantity=data.quantity,
                            updated_at=timestamp,
                        )
                    )
                    continue
                record.name = data.name
                record.price = data.price
                record.quantity = data.quantity
                record.updated_at = timestamp

    @staticmethod
    def _to_product(record: ProductRecord) -> Product:
        return Product(
            sku=record.sku,
            name=record.name,
            price=record.price,
            quantity=record.quantity,
            updated_at=record.updated_at,
        )
