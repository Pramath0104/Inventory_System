from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document, Indexed, Link
from pydantic import EmailStr

from src.customers.models import Customer

class RoleEnum(str, Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"

class User(Document):
    name: str
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    role: RoleEnum = RoleEnum.customer
    created_at: datetime = datetime.utcnow()
    
    # Nullable customer reference (acting as a "foreign key" link in MongoDB)
    customer: Optional[Link[Customer]] = None

    class Settings:
        name = "users"
