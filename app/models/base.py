from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

class BaseModel(object):
    """Базовая модель с общими полями"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
