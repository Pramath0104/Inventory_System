import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

test_state = {}

async def test_auth_endpoints(customer_client: AsyncClient):
    resp = await customer_client.get("/auth/me")
    assert resp.status_code == 200
    # Customer doesn't get their customer_id from /auth/me in this API design
    # We will fetch it using admin_client in the next test

async def test_category_endpoints(customer_client: AsyncClient, admin_client: AsyncClient):
    # Need to create a category first as admin to test GET
    payload = {"name": "Customer Category", "description": "Category for customer tests"}
    c_resp = await admin_client.post("/categories/", json=payload)
    cat_id = c_resp.json().get("id") or c_resp.json().get("_id")
    test_state["category_id"] = cat_id

    # POST /categories/ (Blocked)
    resp = await customer_client.post("/categories/", json=payload)
    assert resp.status_code == 403

    # GET /categories/ (Allowed)
    resp = await customer_client.get("/categories/")
    assert resp.status_code == 200

    # GET /categories/{id} (Allowed)
    resp = await customer_client.get(f"/categories/{test_state['category_id']}")
    assert resp.status_code == 200

    # Fetch the customer's ID via Admin since customer can't read /customers/
    cust_resp = await admin_client.get("/customers/")
    customer_list = cust_resp.json()
    my_cust = next((c for c in customer_list if c["email"] == "customer@inventory.com"), None)
    test_state["user_customer_id"] = my_cust.get("id") or my_cust.get("_id")

async def test_product_endpoints(customer_client: AsyncClient, admin_client: AsyncClient):
    # Create product as admin
    payload = {
        "name": "Customer Product",
        "description": "Product for customer test",
        "category_id": test_state["category_id"],
        "price": 19.99,
        "stock_quantity": 20,
        "sku": "CUST-SKU-1"
    }
    p_resp = await admin_client.post("/products/", json=payload)
    prod_id = p_resp.json().get("id") or p_resp.json().get("_id")
    test_state["product_id"] = prod_id

    # POST /products/ (Blocked)
    resp = await customer_client.post("/products/", json=payload)
    assert resp.status_code == 403

    # GET /products/ (Allowed)
    resp = await customer_client.get("/products/")
    assert resp.status_code == 200

    # GET /products/{id} (Allowed)
    resp = await customer_client.get(f"/products/{test_state['product_id']}")
    assert resp.status_code == 200

    # PATCH /products/{id} (Blocked)
    resp = await customer_client.patch(f"/products/{test_state['product_id']}", json={"price": 25.99})
    assert resp.status_code == 403

    # GET low-stock (Blocked)
    resp = await customer_client.get("/products/low-stock?threshold=100")
    assert resp.status_code == 403

async def test_customer_endpoints(customer_client: AsyncClient):
    # POST /customers/ (Blocked)
    payload = {"name": "Another Customer", "email": "another@example.com"}
    resp = await customer_client.post("/customers/", json=payload)
    assert resp.status_code == 403

    # GET /customers/ (Blocked)
    resp = await customer_client.get("/customers/")
    assert resp.status_code == 403

    # GET /customers/{id} (Blocked for any id via global block)
    resp = await customer_client.get(f"/customers/{test_state['user_customer_id']}")
    assert resp.status_code == 403

async def test_order_endpoints(customer_client: AsyncClient):
    # POST /orders/ for self (Allowed)
    payload = {
        "customer_id": test_state["user_customer_id"],
        "items": [
            {"product_id": test_state["product_id"], "quantity": 1}
        ]
    }
    resp = await customer_client.post("/orders/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    test_state["order_id"] = data.get("id") or data.get("_id")

    # POST /orders/ for someone else (Blocked)
    bad_payload = payload.copy()
    bad_payload["customer_id"] = test_state["category_id"] # Just use random ID
    resp = await customer_client.post("/orders/", json=bad_payload)
    assert resp.status_code == 403

    # GET /orders/ (Allowed - should only return their own)
    resp = await customer_client.get("/orders/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # GET /orders/{id} (Allowed for own order)
    resp = await customer_client.get(f"/orders/{test_state['order_id']}")
    assert resp.status_code == 200

    # Cancel (Blocked)
    resp = await customer_client.post(f"/orders/{test_state['order_id']}/cancel")
    assert resp.status_code == 403

async def test_inventory_log_endpoints(customer_client: AsyncClient):
    # GET /inventory-log/{product_id} (Blocked)
    resp = await customer_client.get(f"/inventory-log/{test_state['product_id']}")
    assert resp.status_code == 403
