import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_invalid_objectid(admin_client: AsyncClient):
    payload = {
        "customer_id": "invalid-object-id",
        "items": [{"product_id": "also-invalid", "quantity": 1}]
    }
    resp = await admin_client.post("/orders/", json=payload)
    # Pydantic should catch malformed ObjectIds and return 422
    assert resp.status_code == 422

async def test_zero_or_negative_quantity(admin_client: AsyncClient):
    # Need a valid object id to pass the object id check
    valid_id = "64b7f8c9b2f3a4e5d6c7b8a9"
    payload = {
        "customer_id": valid_id,
        "items": [{"product_id": valid_id, "quantity": 0}]
    }
    resp = await admin_client.post("/orders/", json=payload)
    assert resp.status_code == 422
    
    payload["items"][0]["quantity"] = -5
    resp = await admin_client.post("/orders/", json=payload)
    assert resp.status_code == 422

async def test_empty_order(admin_client: AsyncClient):
    valid_id = "64b7f8c9b2f3a4e5d6c7b8a9"
    payload = {
        "customer_id": valid_id,
        "items": []
    }
    resp = await admin_client.post("/orders/", json=payload)
    assert resp.status_code == 422
