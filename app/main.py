from fastapi import FastAPI

app = FastAPI(
    title="Key Manager",
    description="Сервис управления ключами доступа (дипломный проект TB1)",
    version="0.1.0",
)

@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "service": "key-manager"}