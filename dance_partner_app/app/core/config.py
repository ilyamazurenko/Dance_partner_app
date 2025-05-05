"""Настройки и конфигурация приложения."""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (если он есть)
load_dotenv()

class Settings(BaseSettings):
    """Основные настройки приложения, загружаемые из переменных окружения."""
    # Настройки приложения
    APP_NAME: str = "Dance Partner Finder API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Настройки базы данных (SQLite)
    # Используем асинхронный драйвер aiosqlite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dance_app.db")

    # Настройки JWT токенов
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "a_very_secret_key_that_should_be_changed"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Токен живет 30 минут

    class Config:
        """Конфигурация Pydantic Settings."""
        case_sensitive = True
# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings() 
