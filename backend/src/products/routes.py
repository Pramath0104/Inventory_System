from fastapi import APIRouter, status, Query, Depends
from typing import List
from beanie import PydanticObjectId
from src.products.dtos import ProductCreate, ProductUpdate, ProductResponse
from src.products import controllers
from src.auth.controllers import require_role
from src.auth.models import RoleEnum

router = APIRouter()

# DTO mapping function
def map_to_response(product) -> ProductResponse:
    # Handle both Link[Category] (has .ref) and raw Category document (has .id directly)
    cat_id = product.category.ref.id if hasattr(product.category, "ref") else product.category.id
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        category_id=cat_id,
        price=product.price,
        stock_quantity=product.stock_quantity,
        sku=product.sku
    )

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def create_product(product_in: ProductCreate):
    product = await controllers.create_product(product_in)
    return map_to_response(product)

@router.get("/", response_model=List[ProductResponse])
async def list_products():
    products = await controllers.get_products()
    return [map_to_response(p) for p in products]

@router.get("/low-stock", response_model=List[ProductResponse], dependencies=[Depends(require_role([RoleEnum.admin]))])
async def get_low_stock(threshold: int = Query(10, ge=0)):
    products = await controllers.get_low_stock_products(threshold)
    return [map_to_response(p) for p in products]

@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: PydanticObjectId):
    product = await controllers.get_product(id)
    return map_to_response(product)

@router.patch("/{id}", response_model=ProductResponse, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def update_product(id: PydanticObjectId, product_in: ProductUpdate):
    product = await controllers.update_product(id, product_in)
    return map_to_response(product)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role([RoleEnum.admin]))])
async def delete_product(id: PydanticObjectId):
    await controllers.delete_product(id)
