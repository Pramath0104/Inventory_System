from pydantic import BaseModel
from typing import List
from datetime import datetime
from beanie import PydanticObjectId

from pydantic import BaseModel, Field

class OrderItemCreate(BaseModel):
    product_id: PydanticObjectId
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_id: PydanticObjectId
    items: List[OrderItemCreate] = Field(..., min_length=1)

class OrderItemResponse(BaseModel):
    id: PydanticObjectId
    product_id: PydanticObjectId
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: PydanticObjectId
    customer_id: PydanticObjectId
    order_date: datetime
    status: str
    total_amount: float
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
