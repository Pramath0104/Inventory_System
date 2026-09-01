from pydantic import BaseModel
from datetime import datetime
from beanie import PydanticObjectId

class InventoryLogResponse(BaseModel):
    id: PydanticObjectId
    product_id: PydanticObjectId
    change_qty: int
    reason: str
    timestamp: datetime

    class Config:
        from_attributes = True
