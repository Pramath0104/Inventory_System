from fastapi import APIRouter, Depends
from typing import List
from beanie import PydanticObjectId
from src.inventory_log.dtos import InventoryLogResponse
from src.inventory_log import controllers
from src.auth.controllers import require_role
from src.auth.models import RoleEnum

router = APIRouter()

def map_to_response(log) -> InventoryLogResponse:
    prod_id = log.product.ref.id if hasattr(log.product, "ref") else log.product.id
    return InventoryLogResponse(
        id=log.id,
        product_id=prod_id,
        change_qty=log.change_qty,
        reason=log.reason,
        timestamp=log.timestamp
    )

@router.get("/{product_id}", response_model=List[InventoryLogResponse], dependencies=[Depends(require_role([RoleEnum.admin]))])
async def get_inventory_log(product_id: PydanticObjectId):
    logs = await controllers.get_logs_by_product(product_id)
    return [map_to_response(log) for log in logs]
