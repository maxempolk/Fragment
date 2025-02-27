from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base


class Like(Base, BaseModel):
    """Модель для лайков фрагментов кода"""
    __tablename__ = "likes"

    fragment_id = Column(Integer, ForeignKey("fragments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Отношения
    fragment = relationship("Fragment", back_populates="likes")
    user = relationship("User", back_populates="likes")

    # Уникальное ограничение: один пользователь - один лайк на фрагмент
    __table_args__ = (
        UniqueConstraint("fragment_id", "user_id", name="unique_user_fragment_like"),
    )
