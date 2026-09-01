from beanie import Document, Link
from pydantic import Field
from datetime import datetime, timezone
from src.products.models import Product

class InventoryLog(Document):
    product: Link[Product]
    change_qty: int
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "inventory_log"
