from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserPublic
from app.schemas.tag import TagResponse


# Базовая схема фрагмента
class FragmentBase(BaseModel):
    title: str
    content: str
    language: str
    description: Optional[str] = None
    is_public: bool = True


# Схема для создания фрагмента
class FragmentCreate(FragmentBase):
    tags: Optional[List[str]] = []


# Схема для обновления фрагмента
class FragmentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


# Схема для отображения фрагмента
class FragmentInDB(FragmentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схема для публичного отображения фрагмента
class FragmentResponse(FragmentInDB):
    author: UserPublic
    tags: List[TagResponse] = []
    likes_count: int
    views_count: int
    is_liked_by_current_user: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


# Схема для списка фрагментов
class FragmentListResponse(BaseModel):
    items: List[FragmentResponse]
    total: int
