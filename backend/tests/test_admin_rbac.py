import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

test_state = {}

async def test_auth_endpoints(admin_client: AsyncClient):
    resp = await admin_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"

async def test_category_endpoints(admin_client: AsyncClient):
    payload = {"name": "Admin Category", "description": "Category for admin"}
    resp = await admin_client.post("/categories/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["category_id"] = data.get("id") or data.get("_id")

    resp = await admin_client.get("/categories/")
    assert resp.status_code == 200

    resp = await admin_client.get(f"/categories/{test_state['category_id']}")
    assert resp.status_code == 200
    
    # Method not allowed (route does not exist)
    resp = await admin_client.delete(f"/categories/{test_state['category_id']}")
    assert resp.status_code == 405

async def test_product_endpoints(admin_client: AsyncClient):
    payload = {
        "name": "Admin Product",
        "description": "Product for admin",
        "category_id": test_state["category_id"],
        "price": 99.99,
        "stock_quantity": 50,
        "sku": "ADMIN-SKU-1"
    }
    resp = await admin_client.post("/products/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["product_id"] = data.get("id") or data.get("_id")

    resp = await admin_client.get("/products/")
    assert resp.status_code == 200

    resp = await admin_client.get(f"/products/{test_state['product_id']}")
    assert resp.status_code == 200

    patch_payload = {"price": 110.99}
    resp = await admin_client.patch(f"/products/{test_state['product_id']}", json=patch_payload)
    assert resp.status_code == 200

    # GET low-stock (Admin allowed)
    resp = await admin_client.get("/products/low-stock?threshold=100")
    assert resp.status_code == 200

    # DELETE /products/{id} (Admin allowed)
    resp = await admin_client.delete(f"/products/{test_state['product_id']}")
    assert resp.status_code == 204

async def test_customer_endpoints(admin_client: AsyncClient):
    payload = {"name": "Admin Test Customer", "email": "admintest@example.com"}
    resp = await admin_client.post("/customers/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["customer_id"] = data.get("id") or data.get("_id")

    resp = await admin_client.get("/customers/")
    assert resp.status_code == 200

    resp = await admin_client.get(f"/customers/{test_state['customer_id']}")
    assert resp.status_code == 200
    
    resp = await admin_client.patch(f"/customers/{test_state['customer_id']}", json={"name": "Admin Updated Customer"})
    assert resp.status_code == 200

    resp = await admin_client.delete(f"/customers/{test_state['customer_id']}")
    assert resp.status_code == 204

async def test_order_endpoints(admin_client: AsyncClient):
    # Need to recreate a product and a customer since admin deleted them!
    # Recreate category
    c_resp = await admin_client.post("/categories/", json={"name": "Temp Cat"})
    cat_id = c_resp.json().get("id") or c_resp.json().get("_id")
    
    # Recreate product
    p_resp = await admin_client.post("/products/", json={"name": "Temp Prod", "category_id": cat_id, "price": 10.0, "stock_quantity": 10, "sku": "TEMP-1"})
    prod_id = p_resp.json().get("id") or p_resp.json().get("_id")
    test_state["product_id"] = prod_id
    
    # Recreate customer
    cu_resp = await admin_client.post("/customers/", json={"name": "Temp Cust", "email": "tempcust@example.com"})
    cust_id = cu_resp.json().get("id") or cu_resp.json().get("_id")
    
    payload = {
        "customer_id": cust_id,
        "items": [
            {"product_id": prod_id, "quantity": 1}
        ]
    }
    resp = await admin_client.post("/orders/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["order_id"] = data.get("id") or data.get("_id")

    resp = await admin_client.get("/orders/")
    assert resp.status_code == 200

    resp = await admin_client.get(f"/orders/{test_state['order_id']}")
    assert resp.status_code == 200

    # Cancel (Admin allowed)
    resp = await admin_client.post(f"/orders/{test_state['order_id']}/cancel")
    assert resp.status_code == 200

async def test_inventory_log_endpoints(admin_client: AsyncClient):
    # GET /inventory-log/{product_id} (Admin allowed)
    resp = await admin_client.get(f"/inventory-log/{test_state['product_id']}")
    assert resp.status_code == 200
