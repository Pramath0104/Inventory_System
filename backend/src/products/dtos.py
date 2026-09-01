from pydantic import BaseModel, Field
from typing import Optional
from beanie import PydanticObjectId

class ProductCreate(BaseModel):
    name: str
    category_id: PydanticObjectId
    price: float = Field(gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    sku: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[PydanticObjectId] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None

class ProductResponse(BaseModel):
    id: PydanticObjectId
    name: str
    category_id: PydanticObjectId
    price: float
    stock_quantity: int
    sku: str

    class Config:
        from_attributes = True
