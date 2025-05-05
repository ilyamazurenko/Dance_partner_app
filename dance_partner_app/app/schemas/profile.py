"""Pydantic схемы для сущности Profile."""

import datetime
from typing import List # standard library first
from pydantic import BaseModel, ConfigDict

# Импортируем схему для чтения DanceStyle, чтобы использовать ее здесь
from .dance_style import DanceStyleRead

# Схема для связи Профиля и Стиля Танца (включая уровень)
class ProfileDanceStyleLink(BaseModel):
    """Схема для представления связи Профиль-Стиль с уровнем."""
    dance_style: DanceStyleRead
    skill_level: str

    model_config = ConfigDict(from_attributes=True)


# Базовая схема для Profile
class ProfileBase(BaseModel):
    """Базовая схема для профиля."""
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    bio: str | None = None
    preferred_contact: str | None = None

# Схема для создания Profile (связь с user_id будет установлена в логике)
class ProfileCreate(ProfileBase):
    """Схема для создания профиля."""
    pass

# Схема для обновления Profile (все поля опциональны)
class ProfileUpdate(ProfileBase):
    """Схема для обновления профиля."""
    dance_style_ids: list[int] | None = None
    pass

# Схема для чтения Profile (из БД)
class ProfileRead(ProfileBase):
    """Схема для чтения профиля, включая связанные стили."""
    id: int
    user_id: int
    created_at: datetime.datetime
    dance_styles: List[DanceStyleRead] = []

    model_config = ConfigDict(from_attributes=True)
