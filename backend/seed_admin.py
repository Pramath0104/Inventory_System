import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from core.config import settings
from src.auth.models import User
from src.auth.controllers import get_password_hash

async def seed_admin():
    print("Connecting to database...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = client[settings.DATABASE_NAME]
    
    await init_beanie(
        database=database,
        document_models=[User]
    )
    
    print("Checking for existing admin...")
    existing_admin = await User.find_one({"role": "admin"})
    
    if existing_admin:
        print(f"Admin already exists: {existing_admin.email}")
        sys.exit(0)
        
    print(f"Creating admin user: {settings.ADMIN_EMAIL}...")
    
    admin_user = User(
        name=settings.ADMIN_NAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        role="admin"
    )
    
    await admin_user.insert()
    print("SUCCESS: Admin user created successfully.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
