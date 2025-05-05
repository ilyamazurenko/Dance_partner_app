from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db_session
from app.schemas.dance_style import DanceStyleCreate, DanceStyleRead
from app.services import dance_styles as styles_service
# Пока не добавляем зависимость от аутентификации для создания стилей
# from app.utils.security import get_current_active_user
# from app.db.models import User

router = APIRouter()

@router.post(
    "/",
    response_model=DanceStyleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dance style"
    # dependencies=[Depends(get_current_active_user)] # Раскомментировать для защиты
)
async def create_new_dance_style(
    style_in: DanceStyleCreate,
    db: AsyncSession = Depends(get_db_session)
    # current_user: User = Depends(get_current_active_user) # Раскомментировать для защиты
):
    """Создает новый танцевальный стиль."""
    try:
        style = await styles_service.create_dance_style(db=db, style_in=style_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return style

@router.get("/", response_model=List[DanceStyleRead], summary="Get all dance styles")
async def get_all_dance_styles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Получает список всех танцевальных стилей с пагинацией."""
    styles = await styles_service.get_dance_styles(db, skip=skip, limit=limit)
    return styles

@router.get("/{style_id}", response_model=DanceStyleRead, summary="Get dance style by ID")
async def get_dance_style_by_id(
    style_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Получает информацию о танцевальном стиле по его ID."""
    style = await styles_service.get_dance_style(db, style_id=style_id)
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dance style not found"
        )
    return style 
