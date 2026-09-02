# Inventory & Order Management System

A highly modular, robust FastAPI backend designed for e-commerce-style inventory and order management, focusing on strict security, data integrity, and complex NoSQL transaction handling.

---

## 🚀 Key Features

- **Product Catalog Management**: Full CRUD capabilities for products and hierarchical categories, including automatic inventory logging on manual stock adjustments.
- **Atomic Order Transactions**: `place_order` safely executes a multi-document transaction that simultaneously deducts product stock, generates an order record, and logs the inventory change. If a concurrent write conflict occurs (e.g. multiple users buying the last unit), an **exponential backoff retry loop** automatically catches the `TransientTransactionError`, retries the transaction safely, and gracefully rejects the order if stock is depleted, completely eliminating race conditions.
- **Order Cancellation**: Authorized users can cancel an order, which atomically updates the order status, restocks the items, and audits the restock in the inventory logs.
- **Inventory Audit Logging**: Every single change to a product's stock—whether from an initial creation, a manual update, an order placement, or a cancellation—is permanently recorded in an immutable audit trail.
- **Low-Stock Reporting**: A dedicated `/low-stock` endpoint allows administrators to query products that have fallen below a customizable stock threshold.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Has full, unrestricted access to all endpoints, including inventory audits and deletions.
  - **Staff**: Can manage products, categories, customers, and orders, but is strictly prohibited from deleting records or viewing the immutable inventory audit logs.
  - **Customer**: A highly restricted role. Customers can browse products and categories, place orders, and view *only their own* past orders.
- **Strict Authentication & Security**:
  - JWT (JSON Web Tokens) for stateless authentication.
  - `bcrypt` password hashing via `passlib`.
  - **Admin-Isolation Security Design**: Admin accounts *cannot* be created via any API endpoint (creating an admin via `/auth/create-staff` returns a 422 error). Admin accounts can only be provisioned directly via the `seed_admin.py` database script running securely on the host infrastructure, completely eliminating network-based privilege escalation.
- **Bulletproof Input Validation**: Utilizing Pydantic models to instantly reject malformed MongoDB `ObjectId`s, empty order payloads (`items: []`), and negative or zero purchase quantities before the database is ever queried. 
- **Database-Level Integrity**: MongoDB explicitly enforces unique indexes on `Customer.email` and `Product.sku` to guarantee no duplicates bypass the application layer.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI (`fastapi==0.141.1`), Starlette (`starlette==1.6.0`)
- **Server:** Uvicorn (`uvicorn==0.52.4`)
- **Database (MongoDB):**
  - ODM: Beanie (`beanie==2.0.0`)
  - Async Driver: Motor (`motor==3.7.1`)
  - Sync Driver (Internal): PyMongo (`pymongo==4.17.0`)
- **Validation & Configuration:** Pydantic (`pydantic==2.13.5`), Pydantic Settings (`pydantic-settings==2.15.0`)
- **Authentication:**
  - JWT Encoding/Decoding: `python-jose==3.5.0`
  - Hashing: `passlib==1.7.4`, `bcrypt==3.2.2`
  - Forms: `python-multipart==0.0.32`
- **Testing:** `pytest==9.1.1`, `pytest-asyncio==1.4.0`, `httpx==0.28.1`

---

## 📂 Project Structure

```text
inventory-system/
├── backend/
│   ├── core/               # App-wide configurations (environment variables, JWT constants)
│   ├── src/                # Modular domains handling all business logic
│   │   ├── auth/           # JWT issuance, user modeling, and RBAC middleware
│   │   ├── categories/     # Product category metadata and lookup table
│   │   ├── customers/      # Customer directory and lookup table
│   │   ├── database/       # (Core DB initialization if extracted, else in main.py)
│   │   ├── inventory_log/  # Immutable audit trail recording history of stock changes
│   │   ├── orders/         # Transaction engine (atomic orders, cancellations, stock deduction)
│   │   └── products/       # Product catalog management, SKU uniqueness, low-stock checks
│   ├── tests/              # Comprehensive pytest suite (RBAC boundaries, concurrency, validation)
│   ├── .env                # Secret environment variables (ignored in Git)
│   ├── .env.example        # Template for environment variables
│   ├── main.py             # FastAPI application instance and router aggregation
│   ├── pytest.ini          # Pytest configuration (asyncio settings)
│   ├── requirements.txt    # Frozen dependency tree for deterministic builds
│   └── seed_admin.py       # Bootstrap script to securely provision the root Admin account
├── .gitignore              # Unified ignore rules (Python, macOS, Node.js)
└── README.md               # Project documentation
```

---

## 🌐 API Endpoints

| Method | Path | Description | Required Role / Auth |
|---|---|---|---|
| **POST** | `/auth/register` | Self-register a new customer account | Public |
| **POST** | `/auth/login` | Authenticate and retrieve JWT token | Public |
| **POST** | `/auth/create-staff` | Provision a new staff account | Admin |
| **GET** | `/auth/me` | Get the profile of the currently logged-in user | Any Authenticated |
| **POST** | `/categories/` | Create a new product category | Admin, Staff |
| **GET** | `/categories/` | List all categories | Public |
| **GET** | `/categories/{id}` | Get a specific category by ID | Public |
| **POST** | `/customers/` | Create a new customer profile manually | Admin, Staff |
| **GET** | `/customers/` | List all customers | Admin, Staff |
| **GET** | `/customers/{id}` | Get a specific customer by ID | Admin, Staff |
| **PATCH** | `/customers/{id}` | Update customer details | Admin, Staff |
| **DELETE** | `/customers/{id}` | Delete a customer | Admin |
| **POST** | `/products/` | Create a new product (initializes stock audit log) | Admin, Staff |
| **GET** | `/products/` | List all products in the catalog | Public |
| **GET** | `/products/low-stock`| Query products falling below a stock threshold | Admin |
| **GET** | `/products/{id}` | Get a specific product by ID | Public |
| **PATCH** | `/products/{id}` | Update product/stock (audits manual stock changes) | Admin, Staff |
| **DELETE** | `/products/{id}` | Delete a product | Admin |
| **POST** | `/orders/` | Place an order (Atomic: deducts stock, creates log) | Customer |
| **GET** | `/orders/` | List orders (Customers see only theirs, Staff/Admin see all) | Admin, Staff, Customer |
| **GET** | `/orders/{id}` | Get specific order details (restricted to owner or staff/admin) | Admin, Staff, Customer |
| **POST** | `/orders/{id}/cancel`| Cancel an order (Atomic: updates status, restocks, logs) | Admin |
| **GET** | `/inventory_log/{id}`| View the immutable stock audit trail for a specific product | Admin |

---

## 🗄️ Database Schema

The database utilizes MongoDB, mapped through Beanie ODM, consisting of the following key collections:

- **`users`**: Manages authentication and RBAC. Contains `name`, `email`, `hashed_password`, `role` (`admin`, `staff`, `customer`), and an optional `Link[Customer]` establishing the relationship between the auth account and the customer profile.
- **`categories`**: A flat taxonomy collection containing `name` and `description`.
- **`customers`**: The customer directory containing `name`, `email` (Unique Index).
- **`products`**: The core catalog item containing `name`, `price`, `stock_quantity`, `sku` (Unique Index), and a `Link[Category]` pointing to the parent category.
- **`orders`**: The transactional record containing `customer_id` (manual PydanticObjectId lookup), `order_date`, `status` (`pending`, `completed`, `cancelled`), `total_amount`, and an embedded list of `items` (which store the `product_id`, `quantity`, and `unit_price` at the time of sale).
- **`inventory_log`**: The immutable ledger for tracking inventory movement. Contains a `Link[Product]`, `change_qty` (+ or -), `reason` (e.g., "Order Placed", "Order Cancelled", "Manual Stock Adjustment"), and a `timestamp`.

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Pramath0104/Inventory_System.git
cd Inventory_System/backend
```

### 2. Setup the virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the template environment file:
```bash
cp .env.example .env
```
Open `.env` and fill in your values:
- `MONGODB_URI`: Your MongoDB Atlas connection string (e.g., `mongodb+srv://...`). Note that your MongoDB cluster **must** be deployed as a Replica Set to support ACID transactions (standard for Atlas).
- `SECRET_KEY`: Generate a secure random string (e.g., `openssl rand -hex 32`) for JWT signing.
- `ADMIN_EMAIL` & `ADMIN_PASSWORD`: Configure the credentials for your initial root admin account.

### 4. Seed the Database
Initialize the root admin account (admins cannot be created via the API):
```bash
PYTHONPATH=. python seed_admin.py
```

### 5. Run the Application
Start the Uvicorn ASGI server:
```bash
uvicorn main:app --reload
```
Navigate to **`http://localhost:8000/docs`** to access the interactive Swagger UI and test the API!

### 6. Run the Test Suite
Ensure your `.env` is configured correctly (the tests create and teardown an isolated `inventory_test_db`).
```bash
PYTHONPATH=. pytest tests/ -v
```

---

## 🔐 Environment Variables

The application requires the following environment variables (reference `.env.example`):

| Variable | Description |
|---|---|
| `PROJECT_NAME` | The title of the FastAPI application (used in Swagger docs). |
| `MONGODB_URI` | Your MongoDB Atlas connection string. **Must support replica sets for ACID transactions.** |
| `DATABASE_NAME` | The name of the database to use (e.g., `inventory_db`). |
| `ENVIRONMENT` | Deployment environment (e.g., `development`, `production`). |
| `SECRET_KEY` | A highly secure, random string used to cryptographically sign JWTs. |
| `ALGORITHM` | The cryptographic algorithm used for JWTs (default: `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | The lifespan of a JWT access token before it expires. |
| `ADMIN_NAME` | The full name of the root admin provisioned by the `seed_admin.py` script. |
| `ADMIN_EMAIL` | The email address (login) for the root admin. |
| `ADMIN_PASSWORD` | The plaintext password for the root admin (which is hashed during seeding). |

---

## 🧪 Testing

The repository includes a comprehensive, fully automated `pytest` test suite located in the `tests/` directory.

To run the suite, ensure you are in the `backend/` directory (where `pytest.ini` resides to configure `asyncio_mode = auto`) and execute:
```bash
PYTHONPATH=. pytest tests/ -v
```

### Test Files & Coverage
- **`conftest.py`**: The backbone of the test suite. It configures the isolated test database, wipes collections between runs, and provides authenticated HTTP clients as shared fixtures (`admin_client`, `staff_client`, `customer_client`).
- **`test_admin_rbac.py`**: Verifies that the Admin role has full, unrestricted access to all endpoints, including deletions and audit logs.
- **`test_staff_rbac.py`**: Validates the Staff role boundaries, ensuring they can manage catalogs and orders but are correctly blocked (`403 Forbidden`) from deleting records or viewing audit logs.
- **`test_customer_rbac.py`**: Verifies that Customers can place orders and view their own history, but are blocked from accessing inventory logs or other users' data.
- **`test_concurrency.py`**: Actively simulates concurrent write collisions (race conditions) to verify the `TransientTransactionError` backoff logic successfully resolves conflicts when allocating scarce inventory.
- **`test_validation.py`**: Tests edge cases, ensuring malformed Object IDs, negative quantities, and empty order arrays are aggressively rejected (`422 Unprocessable Entity`) before interacting with the database.

---

## 🧠 Design Decisions

- **Embedded Items in Orders**: Unlike traditional SQL relational databases which would use a separate `order_items` table, we embed a list of `OrderItem` models directly inside the `Order` document. This aligns perfectly with MongoDB's document-oriented architecture, ensuring that fetching an order requires only a single high-speed database read, while guaranteeing the entire order (and its items) updates atomically.
- **Admin Network Isolation**: The `admin` role is the highest privilege level, capable of deleting catalog items and cancelling arbitrary orders. To completely eliminate the risk of network-based privilege escalation vulnerabilities, there is intentionally **no API endpoint** capable of creating an admin. The root admin can only be bootstrapped by running `seed_admin.py` directly against the server infrastructure.
- **Atomic Partial Failure Rollbacks**: The `place_order` workflow uses MongoDB's multi-document transactions. If the transaction fails midway (e.g., deducting stock succeeds, but order creation fails, or another concurrent request grabs the last unit), the entire block is aborted. No stock is deducted without an order being created, and no order is created without stock being accurately deducted.

---

## 🔮 Future Improvements

While the backend is highly robust, several areas remain for future expansion:
- **Frontend UI Integration**: Building a React or Next.js frontend to visually consume the REST API and provide an admin dashboard.
- **Pagination, Search, & Filtering**: Extending the `GET /products` endpoint to include query parameters for searching by name, sorting by price, and paginating large catalogs.
- **Rate Limiting**: Implementing a middleware (such as `slowapi`) to throttle login attempts and prevent brute-force or DDoS attacks.
- **CI/CD Pipeline**: Adding GitHub Actions to automatically run the test suite and deploy to a cloud provider on successful pushes.
