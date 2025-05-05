"""Модели данных SQLAlchemy для базы данных приложения."""

import datetime
from typing import List

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Table
)
from sqlalchemy.orm import relationship, Mapped

from .session import Base

# Ассоциативная таблица для связи многие-ко-многим
# между профилями (Profile) и танцевальными стилями (DanceStyle)
profile_dance_style_association = Table(
    'profile_dance_style_association',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('profiles.id'), primary_key=True),
    Column('dance_style_id', Integer, ForeignKey('dance_styles.id'), primary_key=True),
    Column('skill_level', String, default='Beginner')
)

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    # Связь один-к-одному с профилем
    profile: Mapped["Profile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

class Profile(Base):
    """Модель профиля пользователя."""
    __tablename__ = "profiles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    first_name: Mapped[str | None] = Column(String, index=True, nullable=True)
    last_name: Mapped[str | None] = Column(String, index=True, nullable=True)
    city: Mapped[str | None] = Column(String, index=True, nullable=True)
    bio: Mapped[str | None] = Column(Text, nullable=True)
    preferred_contact: Mapped[str | None] = Column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)

    # Связь с пользователем
    user: Mapped["User"] = relationship(back_populates="profile")

    # Связь многие-ко-многим со стилями танцев
    dance_styles: Mapped[List["DanceStyle"]] = relationship(
        secondary=profile_dance_style_association,
        back_populates="profiles",
        lazy="selectin"
    )

class DanceStyle(Base):
    """Модель танцевального стиля."""
    __tablename__ = "dance_styles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    description: Mapped[str | None] = Column(Text, nullable=True)

    # Связь с профилями
    profiles: Mapped[List["Profile"]] = relationship(
        secondary=profile_dance_style_association,
        back_populates="dance_styles"
    ) 
