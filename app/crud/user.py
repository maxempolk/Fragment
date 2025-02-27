from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    """Получить пользователя по имени пользователя"""
    return db.query(User).filter(User.username == username).first()


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user


def create(db: Session, user_create: UserCreate) -> User:
    """Создание нового пользователя"""
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        bio=user_create.bio,
        is_active=user_create.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """Обновление пользователя"""
    update_data = user_update.model_dump(exclude_unset=True)

    # Если передан пароль, хешируем его
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(db: Session, db_user: User) -> bool:
    """Удаление пользователя"""
    db.delete(db_user)
    db.commit()
    return True
