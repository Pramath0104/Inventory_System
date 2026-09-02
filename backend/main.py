from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pymongo.errors import DuplicateKeyError
from contextlib import asynccontextmanager

from core.config import settings
from src.database.session import init_db
from src.products.routes import router as products_router
from src.orders.routes import router as orders_router
from src.inventory_log.routes import router as inventory_log_router
from src.auth.routes import router as auth_router
from src.categories.routes import router as categories_router
from src.customers.routes import router as customers_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Database...")
    await init_db()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(DuplicateKeyError)
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    return JSONResponse(
        status_code=400,
        content={"detail": "A record with that unique identifier already exists."},
    )

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(categories_router, prefix="/categories", tags=["Categories"])
app.include_router(customers_router, prefix="/customers", tags=["Customers"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(inventory_log_router, prefix="/inventory-log", tags=["Inventory Log"])

@app.get("/", include_in_schema=False)
async def root():
    """Redirects the root URL to the API documentation."""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
