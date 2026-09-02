from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException
from src.orders.models import Order, OrderItem
from src.orders.dtos import OrderCreate
from src.customers.models import Customer
from src.products.models import Product
from src.inventory_log.models import InventoryLog
import asyncio
from pymongo.errors import PyMongoError

MAX_RETRIES = 3

async def place_order(order_in: OrderCreate) -> Order:
    customer = await Customer.get(order_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    client = Order.get_pymongo_collection().database.client
    
    for attempt in range(MAX_RETRIES):
        try:
            async with await client.start_session() as session:
                async with session.start_transaction():
                    total_amount = 0.0
                    order_items_links = []
                    
                    # Aggregate required quantities in case the same item is passed multiple times
                    required_qty = {}
                    for item_in in order_in.items:
                        pid = str(item_in.product_id)
                        required_qty[pid] = required_qty.get(pid, 0) + item_in.quantity
                    
                    for pid, qty in required_qty.items():
                        product = await Product.get(PydanticObjectId(pid), session=session)
                        if not product:
                            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
                        
                        if product.stock_quantity < qty:
                            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
                        
                        # Deduct stock
                        product.stock_quantity -= qty
                        await product.save(session=session)
                        
                        # Create OrderItem
                        order_item = OrderItem(
                            product=product,
                            quantity=qty,
                            unit_price=product.price
                        )
                        await order_item.insert(session=session)
                        
                        total_amount += product.price * qty
                        order_items_links.append(order_item)
                        
                        # Log inventory change
                        log = InventoryLog(
                            product=product,
                            change_qty=-qty,
                            reason="Order Placed"
                        )
                        await log.insert(session=session)
                        
                    order = Order(
                        customer=customer,
                        total_amount=total_amount,
                        items=order_items_links,
                        status="completed"
                    )
                    await order.insert(session=session)
                    return order
        except PyMongoError as exc:
            if exc.has_error_label("TransientTransactionError"):
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))
                    continue
            raise

async def get_orders(customer_id: PydanticObjectId | None = None) -> List[Order]:
    if customer_id:
        orders = await Order.find(Order.customer.id == customer_id).to_list()
    else:
        orders = await Order.find_all().to_list()
        
    for order in orders:
        item_ids = [i.ref.id if hasattr(i, "ref") else i.id for i in order.items]
        if item_ids:
            order.items = await OrderItem.find({"_id": {"$in": item_ids}}).to_list()
    return orders

async def get_order(order_id: PydanticObjectId) -> Order:
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item_ids = [i.ref.id if hasattr(i, "ref") else i.id for i in order.items]
    if item_ids:
        order.items = await OrderItem.find({"_id": {"$in": item_ids}}).to_list()
    return order

async def cancel_order(order_id: PydanticObjectId) -> Order:
    client = Order.get_pymongo_collection().database.client
    
    for attempt in range(MAX_RETRIES):
        try:
            async with await client.start_session() as session:
                async with session.start_transaction():
                    order = await Order.get(order_id, session=session)
                    if not order:
                        raise HTTPException(status_code=404, detail="Order not found")
                        
                    if order.status == "cancelled":
                        raise HTTPException(status_code=400, detail="Order is already cancelled")
                    
                    # Manually fetch items to bypass fetch_links=True bug
                    item_ids = [i.ref.id if hasattr(i, "ref") else i.id for i in order.items]
                    if item_ids:
                        order.items = await OrderItem.find({"_id": {"$in": item_ids}}, session=session).to_list()
                    
                    # Restore stock
                    for item in order.items:
                        # item.product is a Link[Product], so we access .ref.id or .id
                        prod_id = item.product.ref.id if hasattr(item.product, "ref") else item.product.id
                        product = await Product.get(prod_id, session=session)
                        if product:
                            product.stock_quantity += item.quantity
                            await product.save(session=session)
                            
                            # Log inventory change
                            log = InventoryLog(
                                product=product,
                                change_qty=item.quantity,
                                reason="Order Cancelled"
                            )
                            await log.insert(session=session)
                            
                    order.status = "cancelled"
                    await order.save(session=session)
                    return order
        except PyMongoError as exc:
            if exc.has_error_label("TransientTransactionError"):
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))
                    continue
            raise
