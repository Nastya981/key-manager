from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет жизненным циклом приложения."""
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    await connect_to_mongo()
    print("MongoDB connected ✅")
    yield
    print("Closing MongoDB connection...")
    await close_mongo_connection()
    print("MongoDB disconnected")


app = FastAPI(
    title="Key Manager",
    description="Сервис управления ключами доступа (дипломный проект TB1)",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "service": "key-manager"}


@app.get("/health/db", tags=["System"])
async def health_db():
    """Проверка подключения к MongoDB."""
    db = get_database()
    result = await db.command("ping")
    return {"status": "ok", "mongodb": result}
