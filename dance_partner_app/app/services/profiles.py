"""Сервисный слой для работы с профилями пользователей."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.models import Profile, User, DanceStyle
from app.schemas.profile import ProfileCreate, ProfileUpdate

async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> Profile | None:
    """Получает профиль пользователя по его ID."""
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.dance_styles))
        .filter(Profile.user_id == user_id)
    )
    return result.scalars().first()

async def get_profile_by_id(db: AsyncSession, profile_id: int) -> Profile | None:
    """Получает профиль по его собственному ID."""
    result = await db.execute(
        select(Profile)
        .options(selectinload(Profile.dance_styles))
        .filter(Profile.id == profile_id)
    )
    return result.scalars().first()


async def create_profile(db: AsyncSession, profile_in: ProfileCreate, user: User) -> Profile:
    """Создает новый профиль для указанного пользователя."""
    existing_profile = await get_profile_by_user_id(db, user_id=user.id)
    if existing_profile:
        raise ValueError("User already has a profile")

    db_profile = Profile(
        **profile_in.model_dump(exclude_unset=True),
        user_id=user.id
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return db_profile

async def update_profile(db: AsyncSession, profile: Profile, profile_in: ProfileUpdate) -> Profile:
    """Обновляет существующий профиль, включая танцевальные стили."""
    update_data = profile_in.model_dump(exclude_unset=True)

    # Извлекаем dance_style_ids, если они есть
    dance_style_ids = update_data.pop('dance_style_ids', None)

    # Обновляем остальные поля профиля
    for key, value in update_data.items():
        setattr(profile, key, value)

    # Обновляем стили, если IDs были переданы
    if dance_style_ids is not None:
        if dance_style_ids: # Если список не пустой
            # Загружаем объекты DanceStyle по ID
            result = await db.execute(
                select(DanceStyle).filter(DanceStyle.id.in_(dance_style_ids))
            )
            styles = result.scalars().all()
            # Проверяем, все ли ID найдены (опционально, но хорошо для надежности)
            if len(styles) != len(dance_style_ids):
                # Можно выбросить ошибку или просто использовать найденные
                pass # Пока просто используем найденные
            profile.dance_styles = styles # SQLAlchemy обработает связи
        else: # Если передан пустой список
            profile.dance_styles = [] # Удаляем все стили

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    # Явно загружаем стили после обновления, чтобы они были в возвращаемом объекте
    await db.refresh(profile, attribute_names=['dance_styles'])
    return profile
 