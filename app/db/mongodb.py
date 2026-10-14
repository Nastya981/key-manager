from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """Устанавливает соединение с MongoDB."""
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DB_NAME]
    await client.admin.command("ping")


async def close_mongo_connection() -> None:
    """Закрывает соединение с MongoDB."""
    global client
    if client is not None:
        client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Возвращает объект базы данных."""
    if database is None:
        raise RuntimeError("MongoDB is not connected")
    return database


def get_collection(name: str):
    """Возвращает коллекцию по имени."""
    return get_database()[name]
