from beanie import Document, Link
from pydantic import Field
from datetime import datetime, timezone
from src.customers.models import Customer
from src.products.models import Product

class OrderItem(Document):
    # order link could be added, but typically in NoSQL we might just link items from Order
    product: Link[Product]
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)

    class Settings:
        name = "order_items"

class Order(Document):
    customer: Link[Customer]
    order_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending" # pending, completed, cancelled
    total_amount: float = Field(default=0.0)
    items: list[Link[OrderItem]] = []

    class Settings:
        name = "orders"
