from typing import Optional
from sqlalchemy.orm import Session

from app.models.like import Like


def get_by_fragment_and_user(
    db: Session,
    fragment_id: int,
    user_id: int
) -> Optional[Like]:
    """Получить лайк по ID фрагмента и ID пользователя"""
    return db.query(Like).filter(
        Like.fragment_id == fragment_id,
        Like.user_id == user_id
    ).first()


def create(
    db: Session,
    fragment_id: int,
    user_id: int
) -> Like:
    """Создать лайк"""
    # Проверяем, существует ли уже такой лайк
    existing_like = get_by_fragment_and_user(db, fragment_id=fragment_id, user_id=user_id)
    if existing_like:
        return existing_like

    # Создаем новый лайк
    db_like = Like(
        fragment_id=fragment_id,
        user_id=user_id
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


def delete(db: Session, db_like: Like) -> bool:
    """Удалить лайк"""
    db.delete(db_like)
    db.commit()
    return True
