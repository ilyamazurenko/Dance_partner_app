"""Pydantic схемы для сущности User."""

from pydantic import BaseModel, EmailStr, ConfigDict

# Базовая схема для User
class UserBase(BaseModel):
    """Базовая схема для пользователя."""
    email: EmailStr

# Схема для создания нового User (требует пароль)
class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str

# Схема для чтения данных User (из БД, без пароля)
class UserRead(UserBase):
    """Схема для чтения данных пользователя."""
    id: int
    is_active: bool

    # Разрешаем загрузку из атрибутов ORM модели
    model_config = ConfigDict(from_attributes=True)
