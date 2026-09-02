from typing import List
from beanie import PydanticObjectId
from src.inventory_log.models import InventoryLog

async def get_logs_by_product(product_id: PydanticObjectId) -> List[InventoryLog]:
    return await InventoryLog.find(InventoryLog.product.id == product_id).to_list()
