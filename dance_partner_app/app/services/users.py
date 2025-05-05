"""Сервисный слой для работы с пользователями."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Получает пользователя из БД по email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Создает нового пользователя в БД."""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user 
