from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from typing import Optional

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerResponse(BaseModel):
    id: PydanticObjectId
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
