import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """
    Асинхронный HTTP-клиент для тестов.
    Использует ASGITransport — FastAPI-приложение вызывается напрямую, без сети.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def registered_user(client):
    """
    Фикстура: регистрирует тестового пользователя и возвращает его данные.
    Email генерируется случайно, чтобы не конфликтовать между запусками.
    """
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"

    response = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text

    return {
        "email": email,
        "password": password,
        "id": response.json()["id"],
    }


@pytest.fixture
async def auth_headers(client, registered_user):
    """
    Фикстура: логинит пользователя и возвращает заголовки с JWT.
    """
    response = await client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
