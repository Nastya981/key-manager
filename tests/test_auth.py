import uuid


async def test_register_success(client):
    """Успешная регистрация возвращает 201 и данные пользователя."""
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": "mypassword123"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert data["is_active"] is True
    assert "password" not in data  # хеш не должен возвращаться


async def test_register_duplicate_email(client):
    """Повторная регистрация с тем же email — 409 Conflict."""
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "mypassword123"}

    r1 = await client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/auth/register", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"]


async def test_register_invalid_email(client):
    """Невалидный email — 422."""
    response = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "mypassword123"},
    )
    assert response.status_code == 422


async def test_register_short_password(client):
    """Пароль короче 8 символов — 422."""
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422


async def test_login_success(client, registered_user):
    """Успешный логин возвращает JWT."""
    response = await client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50


async def test_login_wrong_password(client, registered_user):
    """Неверный пароль — 401, одинаковое сообщение об ошибке."""
    response = await client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


async def test_login_unknown_email(client):
    """Неизвестный email — 401 с тем же сообщением (не утекает информация)."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "somepassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
