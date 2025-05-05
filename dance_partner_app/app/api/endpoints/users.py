from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db_session
from app.schemas.user import UserCreate, UserRead
from app.services import users as users_service
from app.api.dependencies import get_current_active_user
from app.db.models import User

router = APIRouter()

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Эндпоинт для регистрации нового пользователя."""
    existing_user = await users_service.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    try:
        user = await users_service.create_user(db=db, user_in=user_in)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return user

@router.get("/me", response_model=UserRead, summary="Get current user")
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Эндпоинт для получения информации о текущем авторизованном пользователе."""
    return current_user 
