import asyncio
import pytest
from typing import AsyncGenerator, Generator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Импортируем наше FastAPI приложение и базовый класс моделей
from app.main import app
from app.db.session import Base, get_db_session
from app.core.config import settings

# Используем отдельную БД в памяти для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.sqlite"

# Создаем движок и сессию специально для тестов
# Используем scope="session" чтобы БД создавалась один раз на всю сессию тестов
@pytest.fixture(scope="session", autouse=True)
async def test_db_setup():
    """Создает и удаляет тестовую базу данных."""
    test_engine = create_async_engine(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield # Тесты выполняются здесь
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

# Фабрика сессий для тестовой БД
TestingSessionLocal = async_sessionmaker(
    bind=create_async_engine(TEST_DATABASE_URL),
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для переопределения сессии БД в тестах."""
    async with TestingSessionLocal() as session:
        yield session

# Переопределяем зависимость get_db_session в приложении на время тестов
app.dependency_overrides[get_db_session] = override_get_db_session

@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создания асинхронного тестового клиента."""
    # Используем ASGITransport для передачи FastAPI приложения в AsyncClient
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac 
