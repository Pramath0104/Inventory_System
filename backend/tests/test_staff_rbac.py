import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

# State storage for IDs created during tests
test_state = {}

async def test_auth_endpoints(staff_client: AsyncClient):
    # GET /auth/me
    resp = await staff_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["role"] == "staff"

async def test_category_endpoints(staff_client: AsyncClient):
    # POST /categories/ (Allowed)
    payload = {"name": "Test Category", "description": "Category for testing"}
    resp = await staff_client.post("/categories/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["category_id"] = data.get("id") or data.get("_id")

    # GET /categories/ (Allowed)
    resp = await staff_client.get("/categories/")
    assert resp.status_code == 200

    # GET /categories/{id} (Allowed)
    resp = await staff_client.get(f"/categories/{test_state['category_id']}")
    assert resp.status_code == 200

    # DELETE /categories/{id} (Blocked - Admin only or Method Not Allowed if undefined)
    resp = await staff_client.delete(f"/categories/{test_state['category_id']}")
    assert resp.status_code in [403, 405]

async def test_product_endpoints(staff_client: AsyncClient):
    # POST /products/ (Allowed)
    payload = {
        "name": "Test Product",
        "description": "Product for testing",
        "category_id": test_state["category_id"],
        "price": 10.99,
        "stock_quantity": 100,
        "sku": "TEST-SKU-1"
    }
    resp = await staff_client.post("/products/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["product_id"] = data.get("id") or data.get("_id")

    # GET /products/ (Allowed)
    resp = await staff_client.get("/products/")
    assert resp.status_code == 200

    # GET /products/{id} (Allowed)
    resp = await staff_client.get(f"/products/{test_state['product_id']}")
    assert resp.status_code == 200

    # PATCH /products/{id} (Allowed)
    patch_payload = {"price": 15.99}
    resp = await staff_client.patch(f"/products/{test_state['product_id']}", json=patch_payload)
    assert resp.status_code == 200

    # GET /products/low-stock (Blocked - Admin only)
    resp = await staff_client.get("/products/low-stock?threshold=10")
    assert resp.status_code == 403

    # DELETE /products/{id} (Blocked - Admin only)
    resp = await staff_client.delete(f"/products/{test_state['product_id']}")
    assert resp.status_code == 403

async def test_customer_endpoints(staff_client: AsyncClient):
    # POST /customers/ (Allowed)
    payload = {"name": "Test Customer", "email": "testcust@example.com"}
    resp = await staff_client.post("/customers/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["customer_id"] = data.get("id") or data.get("_id")

    # GET /customers/ (Allowed)
    resp = await staff_client.get("/customers/")
    assert resp.status_code == 200

    # GET /customers/{id} (Allowed)
    resp = await staff_client.get(f"/customers/{test_state['customer_id']}")
    assert resp.status_code == 200
    
    # PATCH /customers/{id} (Allowed)
    resp = await staff_client.patch(f"/customers/{test_state['customer_id']}", json={"name": "Updated Customer"})
    assert resp.status_code == 200

    # DELETE /customers/{id} (Blocked - Admin only)
    resp = await staff_client.delete(f"/customers/{test_state['customer_id']}")
    assert resp.status_code == 403

async def test_order_endpoints(staff_client: AsyncClient):
    # POST /orders/ (Allowed? Actually staff doesn't need to place orders, but let's test)
    # The route has no require_role, so anyone can hit it.
    payload = {
        "customer_id": test_state["customer_id"],
        "items": [
            {"product_id": test_state["product_id"], "quantity": 1}
        ]
    }
    resp = await staff_client.post("/orders/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["order_id"] = data.get("id") or data.get("_id")

    # GET /orders/ (Allowed)
    resp = await staff_client.get("/orders/")
    assert resp.status_code == 200

    # GET /orders/{id} (Allowed)
    resp = await staff_client.get(f"/orders/{test_state['order_id']}")
    assert resp.status_code == 200

    # POST /orders/{id}/cancel (Blocked - Admin only)
    resp = await staff_client.post(f"/orders/{test_state['order_id']}/cancel")
    assert resp.status_code == 403

async def test_inventory_log_endpoints(staff_client: AsyncClient):
    # GET /inventory-log/{product_id} (Blocked - Admin only)
    resp = await staff_client.get(f"/inventory-log/{test_state['product_id']}")
    assert resp.status_code == 403
