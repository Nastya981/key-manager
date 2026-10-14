from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.db.mongodb import get_collection
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(user_data: UserRegister) -> UserResponse:
    """
    Регистрирует нового пользователя.
    Проверяет, что email не занят. Хеширует пароль.
    """
    users = get_collection("users")

    # Проверяем, что email не занят
    existing = await users.find_one({"email": user_data.email})
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Хешируем пароль
    hashed = hash_password(user_data.password)

    # Создаём документ
    now = datetime.utcnow()
    doc = {
        "email": user_data.email,
        "hashed_password": hashed,
        "created_at": now,
        "is_active": True,
    }

    # Сохраняем в MongoDB
    result = await users.insert_one(doc)

    return UserResponse(
        id=str(result.inserted_id),
        email=user_data.email,
        created_at=now,
        is_active=True,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход и получение JWT",
)
async def login(user_data: UserLogin) -> TokenResponse:
    """
    Проверяет email и пароль. Возвращает JWT-токен.
    """
    users = get_collection("users")

    # Ищем пользователя
    user = await users.find_one({"email": user_data.email})

    # ВАЖНО: одинаковое сообщение для "не найден" и "неверный пароль" —
    # чтобы нельзя было перебором узнать, какие email зарегистрированы.
    if user is None or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # Создаём JWT
    access_token = create_access_token(str(user["_id"]))

    return TokenResponse(access_token=access_token)
