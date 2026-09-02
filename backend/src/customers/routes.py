from typing import List
from fastapi import APIRouter, Depends, status
from beanie import PydanticObjectId

from src.auth.models import RoleEnum
from src.auth.controllers import require_role
from src.customers.models import Customer
from src.customers.dtos import CustomerCreate, CustomerUpdate
from src.customers.controllers import (
    create_customer,
    get_customers,
    get_customer,
    update_customer,
    delete_customer
)

router = APIRouter()

@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def create_customer_route(customer_in: CustomerCreate):
    return await create_customer(customer_in)

@router.get("/", response_model=List[Customer], dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def get_customers_route():
    return await get_customers()

@router.get("/{customer_id}", response_model=Customer, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def get_customer_route(customer_id: PydanticObjectId):
    return await get_customer(customer_id)

@router.patch("/{customer_id}", response_model=Customer, dependencies=[Depends(require_role([RoleEnum.admin, RoleEnum.staff]))])
async def update_customer_route(customer_id: PydanticObjectId, customer_in: CustomerUpdate):
    return await update_customer(customer_id, customer_in)

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role([RoleEnum.admin]))])
async def delete_customer_route(customer_id: PydanticObjectId):
    await delete_customer(customer_id)
