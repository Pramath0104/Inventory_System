import pytest
import asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_concurrent_orders_for_last_item(admin_client: AsyncClient):
    """
    Test that when two users simultaneously try to buy the last item of a product,
    only one succeeds and the other fails cleanly with a 400 error.
    This proves that TransientTransactionError is being caught and handled, 
    and that no double-deductions occur.
    """
    # 1. Setup Data
    c_resp = await admin_client.post("/categories/", json={"name": "Concurrency Cat"})
    cat_id = c_resp.json().get("id") or c_resp.json().get("_id")

    # Product with EXACTLY 1 stock
    p_resp = await admin_client.post("/products/", json={
        "name": "Golden Ticket", 
        "category_id": cat_id, 
        "price": 100.0, 
        "stock_quantity": 1, 
        "sku": "GOLD-1"
    })
    prod_id = p_resp.json().get("id") or p_resp.json().get("_id")

    # Customers
    cu1_resp = await admin_client.post("/customers/", json={"name": "Alice", "email": "alice@concurrent.com"})
    cust1_id = cu1_resp.json().get("id") or cu1_resp.json().get("_id")

    cu2_resp = await admin_client.post("/customers/", json={"name": "Bob", "email": "bob@concurrent.com"})
    cust2_id = cu2_resp.json().get("id") or cu2_resp.json().get("_id")

    # 2. Prepare simultaneous requests
    payload1 = {
        "customer_id": cust1_id,
        "items": [{"product_id": prod_id, "quantity": 1}]
    }
    
    payload2 = {
        "customer_id": cust2_id,
        "items": [{"product_id": prod_id, "quantity": 1}]
    }

    # Helper function to fire request
    async def place_order(payload):
        return await admin_client.post("/orders/", json=payload)

    # 3. Fire requests concurrently
    results = await asyncio.gather(
        place_order(payload1),
        place_order(payload2)
    )

    # 4. Assertions
    status_codes = [resp.status_code for resp in results]
    
    # We expect exactly one 201 Created and exactly one 400 Bad Request
    assert 201 in status_codes, f"Expected one success, got: {status_codes}"
    assert 400 in status_codes, f"Expected one failure, got: {status_codes}"
    
    # Ensure no 500s occurred
    assert 500 not in status_codes, f"TransientTransactionError leaked out! Got 500."

    # 5. Verify database state
    p_check = await admin_client.get(f"/products/{prod_id}")
    final_stock = p_check.json()["stock_quantity"]
    assert final_stock == 0, "Stock should be exactly 0, no negative stock allowed."
