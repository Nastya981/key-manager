from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения.

    Критичные значения (MONGODB_URL, MONGODB_DB_NAME, SECRET_KEY) обязательны —
    без них приложение не запустится, чтобы случайно не уйти в продакшен
    с дефолтным SECRET_KEY.
    """

    # Обязательные — без значений по умолчанию
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    SECRET_KEY: str

    # Не критичные — с разумными дефолтами
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
