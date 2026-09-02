from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException
from src.customers.models import Customer
from src.customers.dtos import CustomerCreate, CustomerUpdate

async def create_customer(customer_in: CustomerCreate) -> Customer:
    existing = await Customer.find_one(Customer.email == customer_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    
    customer = Customer(**customer_in.model_dump())
    await customer.insert()
    return customer

async def get_customers() -> List[Customer]:
    return await Customer.find_all().to_list()

async def get_customer(customer_id: PydanticObjectId) -> Customer:
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

async def update_customer(customer_id: PydanticObjectId, customer_in: CustomerUpdate) -> Customer:
    customer = await get_customer(customer_id)
    update_data = customer_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(customer, key, value)
        
    await customer.save()
    return customer

async def delete_customer(customer_id: PydanticObjectId):
    customer = await get_customer(customer_id)
    await customer.delete()
