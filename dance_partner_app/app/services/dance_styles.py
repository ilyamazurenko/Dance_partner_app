"""Сервисный слой для работы с танцевальными стилями."""

from typing import List # standard library first

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import DanceStyle
from app.schemas.dance_style import DanceStyleCreate

async def get_dance_style(db: AsyncSession, style_id: int) -> DanceStyle | None:
    """Получает танцевальный стиль по ID."""
    result = await db.execute(select(DanceStyle).filter(DanceStyle.id == style_id))
    return result.scalars().first()

async def get_dance_style_by_name(db: AsyncSession, name: str) -> DanceStyle | None:
    """Получает танцевальный стиль по имени."""
    result = await db.execute(select(DanceStyle).filter(DanceStyle.name == name))
    return result.scalars().first()

async def get_dance_styles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[DanceStyle]:
    """Получает список танцевальных стилей с пагинацией."""
    result = await db.execute(
        select(DanceStyle).offset(skip).limit(limit)
    )
    return list(result.scalars().all())

async def create_dance_style(db: AsyncSession, style_in: DanceStyleCreate) -> DanceStyle:
    """Создает новый танцевальный стиль."""
    existing_style = await get_dance_style_by_name(db, name=style_in.name)
    if existing_style:
        raise ValueError(f"Dance style with name '{style_in.name}' already exists.")

    db_style = DanceStyle(**style_in.model_dump())
    db.add(db_style)
    await db.commit()
    await db.refresh(db_style)
    return db_style 
