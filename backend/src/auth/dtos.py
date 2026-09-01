from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from src.auth.models import RoleEnum

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.customer

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: PydanticObjectId
    name: str
    email: EmailStr
    role: RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str
