"""Сервисный слой для аутентификации пользователей."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.services import users as users_service # Импортируем сервис пользователей
from app.utils.security import verify_password

async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """Аутентифицирует пользователя по email и паролю."""
    user = await users_service.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 
