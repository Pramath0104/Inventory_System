from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings

# We will import models here to pass them to init_beanie
# This function will be called on FastAPI startup
async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = client[settings.DATABASE_NAME]

    # Import models here to avoid circular imports if needed, 
    # or import at the top of the file once they are created.
    from src.categories.models import Category
    from src.products.models import Product
    from src.customers.models import Customer
    from src.orders.models import Order, OrderItem
    from src.inventory_log.models import InventoryLog
    from src.auth.models import User

    await init_beanie(
        database=database,
        document_models=[
            Category,
            Product,
            Customer,
            Order,
            OrderItem,
            InventoryLog,
            User
        ]
    )
