"""Настройки и утилиты для работы с сессией базы данных SQLAlchemy."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Создаем асинхронный движок SQLAlchemy
async_engine = create_async_engine(
    settings.DATABASE_URL,
)

# Создаем фабрику асинхронных сессий
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для декларативных моделей SQLAlchemy
Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI для получения асинхронной сессии БД."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Инициализирует базу данных, создавая все таблицы."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 
