from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from src.orders.dtos import OrderCreate, OrderResponse, OrderItemResponse
from src.orders import controllers
from src.auth.controllers import require_role, get_current_user
from src.auth.models import User, RoleEnum

router = APIRouter()

def map_to_response(order) -> OrderResponse:
    items_response = []
    for item in order.items:
        prod_id = item.product.ref.id if hasattr(item.product, "ref") else item.product.id
        items_response.append(
            OrderItemResponse(
                id=item.id,
                product_id=prod_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
        )
        
    cust_id = order.customer.ref.id if hasattr(order.customer, "ref") else order.customer.id
    
    return OrderResponse(
        id=order.id,
        customer_id=cust_id,
        order_date=order.order_date,
        status=order.status,
        total_amount=order.total_amount,
        items=items_response
    )

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(order_in: OrderCreate, current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.customer:
        if not current_user.customer or str(order_in.customer_id) != str(current_user.customer.ref.id):
            raise HTTPException(status_code=403, detail="Cannot create order for another customer")
            
    order = await controllers.place_order(order_in)
    # Refetch with links to ensure everything is loaded for response
    order_with_links = await controllers.get_order(order.id)
    return map_to_response(order_with_links)

@router.get("/", response_model=List[OrderResponse])
async def list_orders(current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.customer:
        if not current_user.customer:
            return []
        orders = await controllers.get_orders(customer_id=current_user.customer.ref.id)
    else:
        orders = await controllers.get_orders()
    return [map_to_response(o) for o in orders]

@router.get("/{id}", response_model=OrderResponse)
async def get_order(id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    order = await controllers.get_order(id)
    if current_user.role == RoleEnum.customer:
        if not current_user.customer or str(order.customer.ref.id) != str(current_user.customer.ref.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return map_to_response(order)

@router.post("/{id}/cancel", response_model=OrderResponse, dependencies=[Depends(require_role([RoleEnum.admin]))])
async def cancel_order(id: PydanticObjectId):
    order = await controllers.cancel_order(id)
    return map_to_response(order)
