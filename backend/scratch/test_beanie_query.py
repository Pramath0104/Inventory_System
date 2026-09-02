import asyncio
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from src.products.models import Product
from src.categories.models import Category
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    await init_beanie(database=client[os.getenv("DATABASE_NAME", "inventory_db")], document_models=[Product, Category])
    
    products = await Product.find_all().to_list()
    cat_id = products[0].category.ref.id if hasattr(products[0].category, "ref") else products[0].category.id
    
    query = []
    query.append({"name": {"$regex": "test", "$options": "i"}})
    query.append(Product.category.id == cat_id)
    
    filtered = await Product.find(*query).sort("-price").to_list()
    print("Mixed query length:", len(filtered))

if __name__ == "__main__":
    asyncio.run(main())
