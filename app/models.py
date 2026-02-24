from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=200)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    quantity: int = Field(ge=0)


class Product(BaseModel):
    model_config = ConfigDict(frozen=True)

    sku: str
    name: str
    price: Decimal
    quantity: int
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    limit: int
    offset: int


class InventoryAdjustment(BaseModel):
    delta: int = Field(description='Positive or negative quantity adjustment')


class InventorySyncRequest(BaseModel):
    source: str = Field(min_length=2, max_length=64)
    records: list[ProductCreate]


class InventorySyncResult(BaseModel):
    source: str
    upserted: int
    timestamp: datetime


class LowStockItem(BaseModel):
    sku: str
    name: str
    quantity: int


class ErrorResponse(BaseModel):
    detail: str
