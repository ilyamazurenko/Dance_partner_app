from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.token import Token
from app.services import auth as auth_service
from app.utils.security import create_access_token

router = APIRouter()

@router.post("/token", response_model=Token, summary="Login for access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """Эндпоинт для получения JWT токена по email и паролю."""
    user = await auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаем токен доступа для пользователя
    access_token = create_access_token(
        subject=user.email # Используем email как идентификатор в токене
    )
    return {"access_token": access_token, "token_type": "bearer"} 
