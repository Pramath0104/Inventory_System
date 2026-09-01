from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException
from src.orders.models import Order, OrderItem
from src.orders.dtos import OrderCreate
from src.customers.models import Customer
from src.products.models import Product
from src.inventory_log.models import InventoryLog

async def place_order(order_in: OrderCreate) -> Order:
    customer = await Customer.get(order_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    total_amount = 0.0
    order_items_links = []
    
    # Ideally, this should be a transaction, but Beanie transactions 
    # require MongoDB replica sets. We'll do it sequentially for this setup.
    for item_in in order_in.items:
        product = await Product.get(item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_in.product_id} not found")
        
        if product.stock_quantity < item_in.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        # Deduct stock
        product.stock_quantity -= item_in.quantity
        await product.save()
        
        # Create OrderItem
        order_item = OrderItem(
            product=product,
            quantity=item_in.quantity,
            unit_price=product.price
        )
        await order_item.insert()
        
        total_amount += product.price * item_in.quantity
        order_items_links.append(order_item)
        
        # Log inventory change
        log = InventoryLog(
            product=product,
            change_qty=-item_in.quantity,
            reason="Order Placed"
        )
        await log.insert()
        
    order = Order(
        customer=customer,
        total_amount=total_amount,
        items=order_items_links,
        status="completed"
    )
    await order.insert()
    return order

async def get_orders(customer_id: PydanticObjectId | None = None) -> List[Order]:
    if customer_id:
        # We find orders linked to this customer
        orders = await Order.find(Order.customer.id == customer_id, fetch_links=True).to_list()
    else:
        orders = await Order.find_all(fetch_links=True).to_list()
    return orders

async def get_order(order_id: PydanticObjectId) -> Order:
    # Need to fetch links
    order = await Order.get(order_id, fetch_links=True)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

async def cancel_order(order_id: PydanticObjectId) -> Order:
    order = await get_order(order_id)
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Order is already cancelled")
    
    # Restore stock
    for item in order.items:
        product = await Product.get(item.ref.id)
        if product:
            product.stock_quantity += item.quantity
            await product.save()
            
            # Log inventory change
            log = InventoryLog(
                product=product,
                change_qty=item.quantity,
                reason="Order Cancelled"
            )
            await log.insert()
            
    order.status = "cancelled"
    await order.save()
    return order
