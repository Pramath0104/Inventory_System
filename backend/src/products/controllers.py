from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException
from src.products.models import Product
from src.products.dtos import ProductCreate, ProductUpdate
from src.categories.models import Category
from src.inventory_log.models import InventoryLog

async def create_product(product_in: ProductCreate) -> Product:
    category = await Category.get(product_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if SKU exists
    existing_product = await Product.find_one(Product.sku == product_in.sku)
    if existing_product:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(
        name=product_in.name,
        category=category,
        price=product_in.price,
        stock_quantity=product_in.stock_quantity,
        sku=product_in.sku
    )
    await product.insert()
    
    if product.stock_quantity > 0:
        log = InventoryLog(
            product=product,
            change_qty=product.stock_quantity,
            reason="Initial Stock on Creation"
        )
        await log.insert()
        
    return product

async def get_products() -> List[Product]:
    return await Product.find_all().to_list()

async def get_product(product_id: PydanticObjectId) -> Product:
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

async def update_product(product_id: PydanticObjectId, product_in: ProductUpdate) -> Product:
    product = await get_product(product_id)
    old_stock = product.stock_quantity
    
    update_data = product_in.model_dump(exclude_unset=True)
    
    if "category_id" in update_data:
        category = await Category.get(update_data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        update_data["category"] = category
        del update_data["category_id"]

    for key, value in update_data.items():
        setattr(product, key, value)
        
    await product.save()
    
    if "stock_quantity" in update_data and product.stock_quantity != old_stock:
        qty_diff = product.stock_quantity - old_stock
        log = InventoryLog(
            product=product,
            change_qty=qty_diff,
            reason="Manual Stock Adjustment"
        )
        await log.insert()
        
    return product

async def delete_product(product_id: PydanticObjectId):
    product = await get_product(product_id)
    await product.delete()

async def get_low_stock_products(threshold: int = 10) -> List[Product]:
    return await Product.find(Product.stock_quantity <= threshold).to_list()
