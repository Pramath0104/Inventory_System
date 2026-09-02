from typing import List
from fastapi import APIRouter, Depends, status
from beanie import PydanticObjectId

from src.auth.models import RoleEnum, User
from src.auth.controllers import get_current_user, require_role
from src.categories.models import Category
from src.categories.dtos import CategoryCreate
from src.categories.controllers import (
    create_category,
    get_categories,
    get_category
)

router = APIRouter()

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def create_category_route(category_in: CategoryCreate):
    return await create_category(category_in)

@router.get("/", response_model=List[Category])
async def get_categories_route():
    return await get_categories()

@router.get("/{category_id}", response_model=Category)
async def get_category_route(category_id: PydanticObjectId):
    return await get_category(category_id)
