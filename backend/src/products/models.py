from beanie import Document, Indexed, Link
from pydantic import Field
from src.categories.models import Category

class Product(Document):
    name: str
    category: Link[Category]
    price: float
    stock_quantity: int = Field(default=0, ge=0)
    sku: Indexed(str, unique=True)

    class Settings:
        name = "products"
