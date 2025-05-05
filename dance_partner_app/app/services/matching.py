"""Сервисный слой для поиска партнеров."""

from typing import List # standard library first

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.models import Profile, profile_dance_style_association, User
from app.schemas.matching import PartnerSearchCriteria

async def find_dance_partners(
    db: AsyncSession, criteria: PartnerSearchCriteria, current_user: User
) -> List[Profile]:
    """Ищет профили танцоров по заданным критериям."""

    query = (
        select(Profile)
        # Сразу загружаем связанные стили, чтобы не делать доп. запросы
        .options(selectinload(Profile.dance_styles))
        # Исключаем профиль текущего пользователя
        .filter(Profile.user_id != current_user.id)
    )

    # Применяем фильтры по критериям
    if criteria.city:
        query = query.filter(Profile.city.ilike(f"%{criteria.city}%"))

    if criteria.dance_style_ids:
        query = (
            query
            .join(profile_dance_style_association)
            .filter(profile_dance_style_association.c.dance_style_id.in_(
                criteria.dance_style_ids)
            )
        )

    query = query.distinct()

    result = await db.execute(query)
    profiles = list(result.scalars().all())

    profiles.sort(key=lambda p: p.created_at, reverse=True)

    return profiles 
