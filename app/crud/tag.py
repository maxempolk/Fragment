from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate


def get_by_id(db: Session, tag_id: int) -> Optional[Tag]:
    """Получение тега по ID"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_by_name(db: Session, name: str) -> Optional[Tag]:
    """Получение тега по имени"""
    return db.query(Tag).filter(Tag.name == name).first()


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> Tuple[List[Tag], int]:
    """Получение списка тегов с пагинацией и поиском"""
    query = db.query(Tag)

    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))

    total = query.count()
    tags = query.order_by(Tag.name).offset(skip).limit(limit).all()

    return tags, total


def create(db: Session, tag_create: TagCreate) -> Tag:
    """Создание нового тега"""
    db_tag = Tag(name=tag_create.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_or_create(db: Session, name: str) -> Tag:
    """Получение существующего тега или создание нового"""
    db_tag = get_by_name(db, name=name)
    if db_tag:
        return db_tag

    db_tag = Tag(name=name)
    db.add(db_tag)
    db.flush()
    return db_tag


def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    """Получение или создание списка тегов"""
    tags: List[Tag] = []
    for name in tag_names:
        name = name.strip().lower()
        if name:  # Проверяем, что имя тега не пустое
            tag = get_or_create(db, name=name)
            tags.append(tag)

    return tags


def delete(db: Session, db_tag: Tag) -> bool:
    """Удаление тега"""
    db.delete(db_tag)
    db.commit()
    return True
