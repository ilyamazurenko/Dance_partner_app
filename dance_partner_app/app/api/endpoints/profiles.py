from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List # Импортируем List для response_model в будущем

from app.db.session import get_db_session
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services import profiles as profiles_service
from app.api.dependencies import get_current_active_user
from app.db.models import User, Profile

router = APIRouter()

@router.get("/me", response_model=ProfileRead, summary="Get current user's profile")
async def get_my_profile(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Получает профиль текущего авторизованного пользователя."""
    profile = await profiles_service.get_profile_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for the current user. Please create one."
        )
    return profile

@router.put("/me", response_model=ProfileRead, summary="Create or update current user's profile")
async def create_or_update_my_profile(
    profile_in: ProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Создает или обновляет профиль текущего пользователя."""
    profile = await profiles_service.get_profile_by_user_id(db, user_id=current_user.id)
    if profile:
        updated_profile = await profiles_service.update_profile(
            db=db, profile=profile, profile_in=profile_in
        )
        return updated_profile
    else:
        profile_create_data = ProfileCreate(**profile_in.model_dump())
        try:
            new_profile = await profiles_service.create_profile(
                db=db, profile_in=profile_create_data, user=current_user
            )
            return new_profile
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.get("/{profile_id}", response_model=ProfileRead, summary="Get profile by ID")
async def get_profile_by_id(
    profile_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Получает публичную информацию о профиле по его ID."""
    profile = await profiles_service.get_profile_by_id(db, profile_id=profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    return profile
