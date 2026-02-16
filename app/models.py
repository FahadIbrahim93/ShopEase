from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=200)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class Product(BaseModel):
    model_config = ConfigDict(frozen=True)

    sku: str
    name: str
    price: float
    quantity: int
    updated_at: datetime


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
