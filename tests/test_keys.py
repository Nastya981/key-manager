import uuid


async def test_create_key_success(client, auth_headers):
    """Создание ключа возвращает 201 и сам ключ (один раз)."""
    response = await client.post(
        "/keys",
        json={"name": "Test Key", "description": "For tests"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["name"] == "Test Key"
    assert data["description"] == "For tests"
    assert "id" in data
    assert "key" in data
    assert len(data["key"]) > 30
    assert data["expires_at"] is None


async def test_create_key_requires_auth(client):
    """Без JWT — 403."""
    response = await client.post("/keys", json={"name": "Test Key"})
    assert response.status_code == 403


async def test_list_keys_empty(client, auth_headers):
    """У нового пользователя нет ключей."""
    response = await client.get("/keys", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_keys_returns_metadata_without_key(client, auth_headers):
    """В списке ключей нет поля key — только метаданные."""
    await client.post("/keys", json={"name": "Key 1"}, headers=auth_headers)
    await client.post("/keys", json={"name": "Key 2"}, headers=auth_headers)

    response = await client.get("/keys", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2

    for item in items:
        assert "id" in item
        assert "name" in item
        assert "is_active" in item
        assert "key" not in item


async def test_get_key_by_id(client, auth_headers):
    """GET /keys/{id} возвращает метаданные одного ключа."""
    created = await client.post(
        "/keys",
        json={"name": "Single Key"},
        headers=auth_headers,
    )
    key_id = created.json()["id"]

    response = await client.get(f"/keys/{key_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == key_id
    assert data["name"] == "Single Key"
    assert "key" not in data


async def test_get_unknown_key_returns_404(client, auth_headers):
    """Несуществующий ID — 404."""
    fake_id = "000000000000000000000000"
    response = await client.get(f"/keys/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


async def test_revoke_key(client, auth_headers):
    """DELETE помечает ключ is_active=False."""
    created = await client.post(
        "/keys",
        json={"name": "To Revoke"},
        headers=auth_headers,
    )
    key_id = created.json()["id"]

    response = await client.delete(f"/keys/{key_id}", headers=auth_headers)
    assert response.status_code == 204

    listing = await client.get("/keys", headers=auth_headers)
    items = listing.json()
    revoked = next(item for item in items if item["id"] == key_id)
    assert revoked["is_active"] is False


async def test_users_isolated_keys(client):
    """Ключи одного пользователя не видны другому."""
    email1 = f"u1_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/auth/register", json={"email": email1, "password": "password123"}
    )
    login1 = await client.post(
        "/auth/login", json={"email": email1, "password": "password123"}
    )
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    email2 = f"u2_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/auth/register", json={"email": email2, "password": "password123"}
    )
    login2 = await client.post(
        "/auth/login", json={"email": email2, "password": "password123"}
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    created = await client.post("/keys", json={"name": "User1 Key"}, headers=headers1)
    key_id = created.json()["id"]

    listing2 = await client.get("/keys", headers=headers2)
    assert listing2.json() == []

    revoke = await client.delete(f"/keys/{key_id}", headers=headers2)
    assert revoke.status_code == 404
