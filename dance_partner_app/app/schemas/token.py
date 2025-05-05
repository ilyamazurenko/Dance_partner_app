"""Pydantic схемы для аутентификации и токенов."""

from pydantic import BaseModel

# Схема для данных внутри JWT токена (используется при декодировании)
class TokenData(BaseModel):
    """Схема для данных, хранящихся внутри JWT токена."""
    email: str | None = None

# Схема для ответа при успешном логине
class Token(BaseModel):
    """Схема для ответа с access токеном."""
    access_token: str
    token_type: str
