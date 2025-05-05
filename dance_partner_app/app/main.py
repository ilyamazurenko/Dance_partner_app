"""Основной файл приложения FastAPI."""

from fastapi import FastAPI

from app.db.session import init_db
from app.db import models

from app.api.endpoints import users as users_router
from app.api.endpoints import auth as auth_router
from app.api.endpoints import profiles as profiles_router
from app.api.endpoints import dance_styles as dance_styles_router
from app.api.endpoints import matching as matching_router

app = FastAPI(
    title="Dance Partner Finder API",
    description="API for finding dance partners.",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    """Корневой эндпоинт."""
    return {"message": "Welcome to the Dance Partner Finder API!"}

@app.on_event("startup")
async def on_startup():
    """Выполняет инициализацию при старте приложения."""
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(profiles_router.router, prefix="/profiles", tags=["Profiles"])
app.include_router(dance_styles_router.router, prefix="/styles", tags=["Dance Styles"])
app.include_router(matching_router.router, prefix="/matching", tags=["Matching"]) 