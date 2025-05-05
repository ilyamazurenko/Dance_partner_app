from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db_session
from app.schemas.matching import PartnerSearchCriteria
from app.schemas.profile import ProfileRead # Используем схему для ответа
from app.services import matching as matching_service
from app.api.dependencies import get_current_active_user
from app.db.models import User

router = APIRouter()

@router.post(
    "/find-partners",
    response_model=List[ProfileRead],
    summary="Find potential dance partners based on criteria",
    dependencies=[Depends(get_current_active_user)] # Защищаем эндпоинт
)
async def find_partners_endpoint(
    criteria: PartnerSearchCriteria,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Эндпоинт для поиска танцевальных партнеров."""
    profiles = await matching_service.find_dance_partners(
        db=db, criteria=criteria, current_user=current_user
    )
    if not profiles:
        return []
    return profiles 
