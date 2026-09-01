from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config import settings
from src.database.session import init_db
from src.products.routes import router as products_router
from src.orders.routes import router as orders_router
from src.inventory_log.routes import router as inventory_log_router
from src.auth.routes import router as auth_router

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

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(inventory_log_router, prefix="/inventory-log", tags=["Inventory Log"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
