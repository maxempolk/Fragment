from sqlalchemy import Integer, Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base

fragment_tag_association = Table(
    "fragment_tag",
    Base.metadata,
    Column("fragment_id", Integer, ForeignKey("fragments.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Tag(Base, BaseModel):
    """Модель для тегов"""
    __tablename__ = "tags"

    name = Column(String(50), nullable=False, unique=True, index=True)

    # Отношения
    fragments = relationship("Fragment", secondary=fragment_tag_association, back_populates="tags")
