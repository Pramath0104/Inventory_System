# Inventory & Order Management System

A highly robust, production-ready **FastAPI** backend designed as a portfolio project. It demonstrates advanced database architecture, secure API design, strict Role-Based Access Control (RBAC), and bulletproof NoSQL transaction handling.

---

## 🚀 Key Features & Capabilities

### 1. Advanced MongoDB ACID Transactions
Handling inventory requires precision to prevent race conditions (e.g., two customers buying the last item at the exact same millisecond). 
- **Atomic Operations**: `place_order` and `cancel_order` endpoints are fully wrapped in MongoDB multi-document ACID transactions. 
  - When an order is placed, the system *simultaneously* creates the order record, deducts the product stock, and generates an immutable inventory audit log.
- **Concurrent Write Conflict Handling**: Engineered with an **exponential backoff retry loop**. If a `TransientTransactionError` occurs due to simultaneous writes, the transaction automatically pauses, retries, and gracefully fails with a `400 Bad Request: Insufficient Stock` instead of crashing the server with a 500 error.

### 2. Strict Role-Based Access Control (RBAC)
The API is secured using JWT (JSON Web Tokens) and bcrypt password hashing, divided strictly into three hierarchical roles:
- **Admin**: Unrestricted access. Can create, read, update, and delete all resources across all endpoints.
- **Staff**: Operational access. Can create and view products, categories, customers, and orders. Strictly prevented from deleting records or accessing sensitive inventory audit logs.
- **Customer**: Highly restricted. Can browse the product catalog and categories, place orders, and view *only their own* past orders. Customers are isolated from seeing other customers' data or modifying the catalog.

### 3. Bulletproof Input Validation & Database Integrity
The system employs multiple layers of defense against bad data:
- **Pydantic Schemas**: 
  - Malformed `ObjectId` strings are intercepted immediately, returning a `422 Unprocessable Entity` before the database is ever queried.
  - Empty orders (`items: []`) are violently rejected.
  - Zero or negative stock quantities are strictly blocked.
- **Database-Level Enforcement**: Unique indexes are provisioned directly in MongoDB for fields like `Customer.email` and `Product.sku`. Even if the API validation is somehow bypassed, the database engine will independently throw a `DuplicateKeyError`.

### 4. Comprehensive Automated Testing
A rigorous asynchronous test suite built with `pytest`, `pytest-asyncio`, and `httpx`:
- Full endpoint coverage across all three RBAC roles (Admin, Staff, Customer).
- **Concurrency Testing**: Explicit tests using `asyncio.gather` that simulate simultaneous HTTP requests competing for a single unit of stock to guarantee the retry loop functions flawlessly.
- Validation boundary testing to ensure 422 errors behave as expected.

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** MongoDB Atlas (Cloud)
- **ODM (Object Document Mapper):** [Beanie](https://beanie-odm.dev/) & Motor (Async Python Driver)
- **Authentication:** JWT with `passlib` (bcrypt) & `python-jose`
- **Testing:** `pytest`, `pytest-asyncio`, `httpx`

---

## 📂 Architecture Overview

The project adheres to a **modular monolith** structure, separating business domains into distinct modules inside `backend/src/`:

- `auth/`: JWT issuance, user modeling, password hashing, and role verification.
- `products/`: Product catalog management and stock tracking.
- `orders/`: The core transaction engine handling order creation, cancellation, and stock deduction.
- `inventory_log/`: An immutable audit trail recording the history of all stock changes.
- `customers/` & `categories/`: Lookup tables providing relational-style structure and metadata.

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
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and configure your keys:
- `MONGODB_URI`: Your MongoDB Atlas connection string (e.g., `mongodb+srv://...`). Note that your MongoDB cluster **must** be deployed as a Replica Set to support ACID transactions (which is standard for Atlas).
- `SECRET_KEY`: Generate a secure random string (e.g., `openssl rand -hex 32`) for JWT signing.

### 4. Run the Application
```bash
uvicorn main:app --reload
```
Navigate to **`http://localhost:8000/docs`** to access the interactive Swagger UI and test the API!

### 5. Run the Test Suite
Ensure your `.env` is configured correctly (the tests create and teardown an isolated `inventory_test_db`).
```bash
PYTHONPATH=. pytest tests/ -v
```

---

## 🗺️ Roadmap
- [x] Core Backend API & Modular Structure
- [x] JWT Authentication & RBAC Enforcement
- [x] Complex MongoDB ACID Transactions & Concurrency Handling
- [x] Deep API Validation & Error Handling
- [x] Automated Testing Suite
- [ ] React/Next.js Frontend Dashboard (Phase 2)
