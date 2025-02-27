from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Базовая схема пользователя
class UserBase(BaseModel):
    username: str
    email: EmailStr
    bio: Optional[str] = None
    is_active: bool = True


# Схема для создания пользователя
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Схема для обновления пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


# Схема для отображения пользователя
class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


# Схема для публичного отображения пользователя
class UserPublic(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схема для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str


# Схема для данных токена
class TokenPayload(BaseModel):
    sub: Optional[int] = None
