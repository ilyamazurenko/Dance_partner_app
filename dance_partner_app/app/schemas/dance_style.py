"""Pydantic схемы для сущности DanceStyle."""

from pydantic import BaseModel, ConfigDict

# Базовая схема для DanceStyle
class DanceStyleBase(BaseModel):
    """Базовая схема для танцевального стиля."""
    name: str
    description: str | None = None

# Схема для создания нового DanceStyle (данные из запроса)
class DanceStyleCreate(DanceStyleBase):
    """Схема для создания танцевального стиля."""
    pass

# Схема для чтения DanceStyle (данные из БД, включая ID)
class DanceStyleRead(DanceStyleBase):
    """Схема для чтения танцевального стиля."""
    id: int

    # Настройка для работы с ORM моделями (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True) 
