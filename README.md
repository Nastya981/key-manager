# Key Manager (TB1)

Сервис управления API-ключами с безопасным хранением (только SHA-256-хеши) и JWT-аутентификацией.

## Описание

Менеджер API-ключей — сервис, который позволяет пользователю:
- Регистрироваться и входить по email и паролю (bcrypt).
- Создавать API-ключи для своих сервисов.
- Видеть список своих ключей без самих ключей.
- Отзывать ключи (мягкое удаление).

Ключевая идея безопасности: при создании ключа пользователь видит его один раз, а в базе хранится только SHA-256-хеш.

## Стек технологий

- FastAPI 0.115
- MongoDB 7.0 (Motor)
- JWT (python-jose)
- bcrypt (passlib)
- Pydantic v2
- pytest, pytest-asyncio, httpx
- Docker, Docker Compose
- Python 3.12

## Запуск

Требования: Docker Desktop, 4+ ГБ свободного места.

Шаги:

- git clone https://github.com/Nastya981/key-manager.git
- cd key-manager
- cp .env.example .env
- docker compose up -d --build

После запуска откройте: http://localhost:8000/docs

Остановка: docker compose down

## API Endpoints

System:
- GET /health
- GET /health/db

Auth:
- POST /auth/register
- POST /auth/login

Keys (требует JWT):
- POST /keys
- GET /keys
- GET /keys/{id}
- DELETE /keys/{id}

## Тесты

Команда:

- docker compose exec api pytest tests/ -v

27 тестов: security (12), auth (7), keys (8). Все проходят.

## Безопасность

- Пароли хешируются bcrypt.
- API-ключи хранятся как SHA-256-хеши.
- JWT HS256, срок жизни 30 минут.
- Изоляция данных по user_id.
- IDOR-защита: 404 при доступе к чужому ключу.

## Структура проекта

app/main.py
app/core/config.py
app/core/security.py
app/db/mongodb.py
app/models/user.py
app/models/key.py
app/api/deps.py
app/api/v1/auth.py
app/api/v1/keys.py
tests/conftest.py
tests/test_security.py
tests/test_auth.py
tests/test_keys.py
Dockerfile
docker-compose.yml
requirements.txt
pytest.ini
README.md

## Бизнес-ценность

- Централизация управления ключами.
- Снижение риска утечек.
- Ускорение онбординга.
- Аудит действий.

## Контекст

Учебный проект — дипломная работа. Проект TB1 «Менеджер ключей».

## Лицензия

Учебный проект.

## Автор

Дипломный проект выполнен в рамках курса Python-разработки.
