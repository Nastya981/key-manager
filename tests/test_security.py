from app.core.security import (
    hash_password,
    verify_password,
    generate_api_key,
    hash_api_key,
    verify_api_key,
    create_access_token,
    decode_access_token,
)


# ============ Хеширование паролей ============

def test_hash_password_returns_string():
    h = hash_password("mypassword")
    assert isinstance(h, str)
    assert h.startswith("$2b$")  # bcrypt-префикс
    assert h != "mypassword"     # не открытый пароль


def test_verify_password_correct():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True


def test_verify_password_wrong():
    h = hash_password("mypassword")
    assert verify_password("wrongpassword", h) is False


def test_hash_password_different_each_time():
    """bcrypt использует соль — один пароль даёт разные хеши."""
    h1 = hash_password("mypassword")
    h2 = hash_password("mypassword")
    assert h1 != h2


# ============ API-ключи ============

def test_generate_api_key_unique():
    keys = {generate_api_key() for _ in range(100)}
    assert len(keys) == 100  # все уникальные


def test_generate_api_key_length():
    """token_urlsafe(32) даёт около 43 символов."""
    key = generate_api_key()
    assert len(key) >= 40


def test_hash_api_key_deterministic():
    """SHA-256 от одного ключа всегда даёт одинаковый хеш."""
    key = "my-api-key"
    h1 = hash_api_key(key)
    h2 = hash_api_key(key)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 — 64 hex-символа


def test_verify_api_key():
    key = generate_api_key()
    h = hash_api_key(key)
    assert verify_api_key(key, h) is True
    assert verify_api_key("wrong-key", h) is False


# ============ JWT ============

def test_create_access_token():
    token = create_access_token("user-123")
    assert isinstance(token, str)
    assert token.count(".") == 2  # три части: header.payload.signature


def test_decode_access_token():
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_invalid_token():
    assert decode_access_token("invalid.token.here") is None


def test_decode_tampered_token():
    """Подпись токена нельзя подделать без SECRET_KEY."""
    token = create_access_token("user-123")
    parts = token.split(".")
    # Меняем payload на другой
    tampered = f"{parts[0]}.eyJzdWIiOiJoYWNrZXIifQ.{parts[2]}"
    assert decode_access_token(tampered) is None
