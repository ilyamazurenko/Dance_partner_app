"""Pydantic схемы для поиска партнеров."""

from typing import List, Optional

from pydantic import BaseModel

# Схема для критериев поиска партнеров
class PartnerSearchCriteria(BaseModel):
    """Схема, описывающая критерии поиска партнеров."""
    city: Optional[str] = None # Город (необязательно)
    dance_style_ids: Optional[List[int]] = None # Список ID желаемых стилей (необязательно)
    min_skill_level: Optional[str] = None # Минимальный уровень (пока строка, можно сделать Enum)
    # Можно добавить другие критерии: пол, возраст и т.д.