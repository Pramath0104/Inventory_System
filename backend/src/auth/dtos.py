from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId
from src.auth.models import RoleEnum

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., max_length=72)
    role: RoleEnum = RoleEnum.customer

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)

class UserResponse(BaseModel):
    id: PydanticObjectId
    name: str
    email: EmailStr
    role: RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str
