import asyncio
from httpx import AsyncClient
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from src.products.models import Product
from src.categories.models import Category
from main import app

load_dotenv()

async def setup_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    await init_beanie(database=client[os.getenv("DATABASE_NAME", "inventory_db")], document_models=[Product, Category])
    
    # Clean up previous tests if any
    await Product.find_all().delete()
    await Category.find_all().delete()
    
    # Create categories
    cat1 = Category(name="Electronics", description="electronic items")
    cat2 = Category(name="Furniture", description="furniture items")
    await cat1.insert()
    await cat2.insert()
    
    # Create products
    p1 = Product(name="Apple iPhone 15", category=cat1, price=999.0, stock_quantity=10, sku="SKU-IPHONE")
    p2 = Product(name="Apple iPad", category=cat1, price=599.0, stock_quantity=20, sku="SKU-IPAD")
    p3 = Product(name="Samsung Galaxy S24", category=cat1, price=899.0, stock_quantity=15, sku="SKU-GALAXY")
    p4 = Product(name="Wooden Table", category=cat2, price=299.0, stock_quantity=5, sku="SKU-TABLE")
    await Product.insert_many([p1, p2, p3, p4])
    
    return cat1.id, cat2.id

async def main():
    cat1_id, cat2_id = await setup_db()
    
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Search by name (case insensitive)
        resp = await client.get("/products/?search=apple")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        print("✅ Search 'apple' returned 2 products.")
        
        # Test 2: Filter by category
        resp = await client.get(f"/products/?category={cat1_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        print("✅ Filter 'Electronics' category returned 3 products.")
        
        # Test 3: Sort by price asc
        resp = await client.get("/products/?sort=asc")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        assert data[0]["price"] == 299.0
        assert data[-1]["price"] == 999.0
        print("✅ Sort by price 'asc' worked perfectly.")
        
        # Test 4: Combined search, category, and sort
        resp = await client.get(f"/products/?search=galaxy&category={cat1_id}&sort=desc")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Samsung Galaxy S24"
        print("✅ Combined query worked perfectly.")

if __name__ == "__main__":
    asyncio.run(main())
