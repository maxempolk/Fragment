from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base


class View(Base, BaseModel):
    """Модель для отслеживания просмотров"""
    __tablename__ = "views"

    fragment_id = Column(Integer, ForeignKey("fragments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Может быть NULL для анонимных просмотров
    ip_address = Column(String(45), nullable=True)  # Для IPv6

    # Отношения
    fragment = relationship("Fragment", back_populates="views")
    user = relationship("User", back_populates="views")
