import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import asyncio

# Override settings before importing the app
from core.config import settings
settings.DATABASE_NAME = "inventory_test_db"

from main import app
from src.auth.models import User, RoleEnum
from src.categories.models import Category
from src.products.models import Product
from src.customers.models import Customer
from src.orders.models import Order, OrderItem
from src.inventory_log.models import InventoryLog
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # Initialize DB for tests
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    # Drop first to prevent duplicate key errors during index creation
    await client.drop_database(settings.DATABASE_NAME)
    
    database = client[settings.DATABASE_NAME]
    await init_beanie(
        database=database,
        document_models=[User, Category, Product, Customer, Order, OrderItem, InventoryLog]
    )
    
    # Clean up DB before tests run to ensure a clean state
    await User.delete_all()
    await Category.delete_all()
    await Product.delete_all()
    await Customer.delete_all()
    await Order.delete_all()
    await OrderItem.delete_all()
    await InventoryLog.delete_all()
    
    yield
    
    # Clean up after all tests complete
    await client.drop_database(settings.DATABASE_NAME)
    client.close()

@pytest_asyncio.fixture(scope="session")
async def async_client():
    # ASGITransport is recommended by httpx for testing FastAPI/ASGI apps
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="session")
async def staff_client(async_client: AsyncClient):
    staff_data = {"name": "Staff User", "email": "staff@inventory.com", "password": "SecretPassword123!", "role": "staff"}
    await async_client.post("/auth/register", json=staff_data)
    login_resp = await async_client.post("/auth/login", data={"username": staff_data["email"], "password": staff_data["password"]})
    token = login_resp.json()["access_token"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def admin_client(async_client: AsyncClient):
    admin_data = {"name": "Admin User", "email": "admin@inventory.com", "password": "SecretPassword123!", "role": "admin"}
    await async_client.post("/auth/register", json=admin_data)
    login_resp = await async_client.post("/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]})
    token = login_resp.json()["access_token"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def customer_client(async_client: AsyncClient):
    customer_data = {"name": "Customer User", "email": "customer@inventory.com", "password": "SecretPassword123!", "role": "customer"}
    await async_client.post("/auth/register", json=customer_data)
    login_resp = await async_client.post("/auth/login", data={"username": customer_data["email"], "password": customer_data["password"]})
    token = login_resp.json()["access_token"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as client:
        yield client
