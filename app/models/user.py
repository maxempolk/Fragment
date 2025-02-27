from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base

class User(Base, BaseModel):
    """Модель пользователя"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Отношения
    fragments = relationship("Fragment", back_populates="author")
    likes = relationship("Like", back_populates="user")
    views = relationship("View", back_populates="user")
