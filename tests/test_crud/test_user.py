# tests/test_crud/test_user.py
from datetime import datetime

from sqlalchemy.orm.session import Session

from app.crud.user import (
    get_by_id, get_by_email, get_by_username, authenticate,
    create, update, delete
)
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.core.security import verify_password

def test_get_by_id(db_session: Session, normal_user: User):
    """Тест получения пользователя по ID"""
    # Вызов тестируемой функции
    retrieved_user = get_by_id(db_session, user_id=normal_user.id)

    # Проверка результата
    assert retrieved_user is not None
    assert retrieved_user.id == normal_user.id
    assert retrieved_user.username == normal_user.username

    # Тест с несуществующим ID
    assert get_by_id(db_session, user_id=9999) is None

def test_get_by_email(db_session: Session, normal_user: User):
    """Тест получения пользователя по email"""
    # Вызов тестируемой функции
    retrieved_user = get_by_email(db_session, email=str(normal_user.email))

    # Проверка результата
    assert retrieved_user is not None
    assert retrieved_user.id == normal_user.id
    assert retrieved_user.email == normal_user.email

    # Тест с несуществующим email
    assert get_by_email(db_session, email="nonexistent@example.com") is None

def test_get_by_username(db_session: Session, normal_user: User):
    """Тест получения пользователя по имени пользователя"""
    # Вызов тестируемой функции
    retrieved_user = get_by_username(db_session, username=str(normal_user.username))

    # Проверка результата
    assert retrieved_user is not None
    assert retrieved_user.id == normal_user.id
    assert retrieved_user.username == normal_user.username

    # Тест с несуществующим username
    assert get_by_username(db_session, username="nonexistent") is None

def test_authenticate(db_session: Session, normal_user: User):
    """Тест аутентификации пользователя"""
    # Вызов тестируемой функции с правильными данными
    authenticated_user = authenticate(
        db_session, email=normal_user.email, password="password123"
    )

    # Проверка результата
    assert authenticated_user is not None
    assert authenticated_user.id == normal_user.id

    # Тест с неправильным паролем
    assert authenticate(db_session, email=normal_user.email, password="wrongpassword") is None

    # Тест с несуществующим email
    assert authenticate(db_session, email="nonexistent@example.com", password="password123") is None

def test_create(db_session: Session):
    """Тест создания пользователя"""
    # Подготовка тестовых данных
    user_create = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="newpassword123",
        bio="New user bio"
    )

    # Вызов тестируемой функции
    created_user = create(db_session, user_create=user_create)

    # Проверка результата
    assert created_user.id is not None
    assert created_user.username == user_create.username
    assert created_user.email == user_create.email
    assert created_user.bio == user_create.bio
    assert hasattr(created_user, "hashed_password")
    assert verify_password(user_create.password, created_user.hashed_password)
    assert created_user.is_active
    assert not created_user.is_admin
    assert isinstance(created_user.created_at, datetime)
    assert isinstance(created_user.updated_at, datetime)

def test_update(db_session: Session, normal_user: User):
    """Тест обновления пользователя"""
    # Подготовка тестовых данных
    user_update = UserUpdate(
        username="updateduser",
        bio="Updated bio",
        password="newpassword123"
    )

    # Вызов тестируемой функции
    updated_user = update(db_session, db_user=normal_user, user_update=user_update)

    # Проверка результата
    assert updated_user.id == normal_user.id
    assert updated_user.username == user_update.username
    assert updated_user.bio == user_update.bio
    assert verify_password(user_update.password, updated_user.hashed_password)
    assert updated_user.updated_at >= updated_user.created_at

    # Тест с частичным обновлением
    partial_update = UserUpdate(bio="New partial bio")
    updated_user = update(db_session, db_user=updated_user, user_update=partial_update)
    assert updated_user.bio == "New partial bio"
    assert updated_user.username == "updateduser"  # Не должно измениться

def test_delete(db_session: Session, normal_user: User):
    """Тест удаления пользователя"""
    # Вызов тестируемой функции
    result = delete(db_session, db_user=normal_user)

    # Проверка результата
    assert result is True
    assert get_by_id(db_session, user_id=normal_user.id) is None
