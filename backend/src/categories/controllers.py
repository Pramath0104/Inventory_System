from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException
from src.categories.models import Category
from src.categories.dtos import CategoryCreate, CategoryUpdate

async def create_category(category_in: CategoryCreate) -> Category:
    existing = await Category.find_one(Category.name == category_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category = Category(**category_in.model_dump())
    await category.insert()
    return category

async def get_categories() -> List[Category]:
    return await Category.find_all().to_list()

async def get_category(category_id: PydanticObjectId) -> Category:
    category = await Category.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
