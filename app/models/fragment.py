from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base
from app.models.tag import fragment_tag_association

class Fragment(Base, BaseModel):
    """Модель фрагмента кода"""
    __tablename__ = "fragments"

    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Отношения
    author = relationship("User", back_populates="fragments")
    likes = relationship("Like", back_populates="fragment", cascade="all, delete-orphan")
    views = relationship("View", back_populates="fragment", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=fragment_tag_association, back_populates="fragments")
