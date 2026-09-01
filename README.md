# Inventory & Order Management System

A highly modular, robust FastAPI backend designed as a portfolio project to demonstrate solid database architecture, secure API design, and complex multi-collection transaction handling.

## Tech Stack
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** MongoDB Atlas (Cloud)
- **ODM (Object Document Mapper):** [Beanie](https://beanie-odm.dev/) & Motor
- **Authentication:** JWT (JSON Web Tokens) with `passlib` (bcrypt)

## Architecture Overview
The project follows a **modular monolith** structure, where business domains are separated into distinct modules inside the `backend/src/` folder:
- `auth`: Handles JWT issuance, password hashing, and role-based access controls (`admin`, `staff`, `customer`).
- `products`: Manages product catalogs and tracks stock levels.
- `orders`: The core transaction engine. Handles atomic-like sequential modifications to deduct stock, log inventory changes, and create order records simultaneously.
- `inventory_log`: An audit trail for every single stock addition or deduction.
- `customers` & `categories`: Lookup tables providing relational-style structure to the NoSQL documents.

## Setup Instructions

1. **Clone and setup the virtual environment:**
```bash
git clone https://github.com/Pramath0104/Inventory_System.git
cd Inventory_System/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Setup Environment Variables:**
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and replace the `MONGODB_URI` placeholder with your actual MongoDB Atlas connection string. You must also generate a secure `SECRET_KEY` for JWT signing.

3. **Run the Application:**
```bash
uvicorn main:app --reload
```
Navigate to `http://localhost:8000/docs` to view the interactive Swagger API documentation and test the endpoints!

## Roadmap
- [x] Core Backend API & Business Logic
- [x] JWT Authentication & Role-Based Access
- [x] Complex Order/Inventory Transaction Logic
- [ ] React Frontend Integration (Phase 2)
