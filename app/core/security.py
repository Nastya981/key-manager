from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Контекст для хеширования паролей через bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============ Пароли пользователей ============

def hash_password(password: str) -> str:
    """Хеширует пароль пользователя."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль хешу."""
    return pwd_context.verify(plain_password, hashed_password)


# ============ API-ключи ============

def generate_api_key() -> str:
    """Генерирует случайный API-ключ (32 байта, URL-safe)."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Хеширует API-ключ (SHA-256) для хранения в БД."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Проверяет, соответствует ли API-ключ хешу."""
    return hash_api_key(api_key) == hashed_key


# ============ JWT-токены ============

def create_access_token(user_id: str) -> str:
    """Создаёт JWT-токен для пользователя."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Декодирует JWT-токен. Возвращает payload или None."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
