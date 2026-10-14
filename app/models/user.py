from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ============ Запросы (что приходит от клиента) ============

class UserRegister(BaseModel):
    """Схема регистрации нового пользователя."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, max_length=72, description="Пароль (8-72 символа)")


class UserLogin(BaseModel):
    """Схема входа пользователя."""
    email: EmailStr
    password: str


# ============ Документ в MongoDB ============

class UserInDB(BaseModel):
    """Как пользователь хранится в MongoDB."""
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


# ============ Ответы API ============

class UserResponse(BaseModel):
    """Что возвращаем клиенту (без хеша пароля)."""
    id: str
    email: EmailStr
    created_at: datetime
    is_active: bool


class TokenResponse(BaseModel):
    """Ответ при успешном логине."""
    access_token: str
    token_type: str = "bearer"
