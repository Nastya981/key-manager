from datetime import datetime
from pydantic import BaseModel, Field


# ============ Запросы ============

class KeyCreate(BaseModel):
    """Схема создания нового API-ключа."""
    name: str = Field(..., min_length=1, max_length=100, description="Название ключа (для какого сервиса)")
    description: str | None = Field(None, max_length=500, description="Опциональное описание")
    expires_at: datetime | None = Field(None, description="Дата истечения (опционально)")


# ============ Документ в MongoDB ============

class KeyInDB(BaseModel):
    """Как ключ хранится в MongoDB."""
    name: str
    description: str | None = None
    hashed_key: str              # SHA-256 хеш самого ключа — в БД храним только хеш!
    user_id: str                 # ID пользователя-владельца
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    is_active: bool = True
    last_used_at: datetime | None = None


# ============ Ответы API ============

class KeyCreatedResponse(BaseModel):
    """
    Ответ при создании ключа.
    ВАЖНО: содержит сам ключ, показывается ОДИН РАЗ при создании!
    """
    id: str
    name: str
    description: str | None = None
    key: str                     # ← сам ключ, только в этом ответе
    created_at: datetime
    expires_at: datetime | None = None


class KeyListItem(BaseModel):
    """Элемент списка ключей — без самого ключа, только метаданные."""
    id: str
    name: str
    description: str | None = None
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool
    last_used_at: datetime | None = None
