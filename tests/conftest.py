# tests/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
# from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

# Настройка тестовой базы данных в памяти
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    """Создает движок SQLAlchemy для тестов"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # Удаляем тестовую БД
    Base.metadata.drop_all(bind=engine)
    os.unlink("./test.db")

@pytest.fixture(scope="function")
def db_session(engine: Engine):
    """Создает новую сессию БД для каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session):
    """Создает тестовый клиент FastAPI"""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def normal_user(db_session: Session):
    """Создает тестового обычного пользователя"""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        bio="Test user bio",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session: Session):
    """Создает тестового пользователя-администратора"""
    user = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        bio="Admin user bio",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def inactive_user(db_session: Session):
    """Создает неактивного тестового пользователя"""
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=get_password_hash("inactive123"),
        bio="Inactive user bio",
        is_active=False,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def normal_user_token(normal_user):
    """Создает токен для обычного пользователя"""
    return create_access_token(subject=normal_user.id)

@pytest.fixture
def admin_user_token(admin_user):
    """Создает токен для администратора"""
    return create_access_token(subject=admin_user.id)

@pytest.fixture
def inactive_user_token(inactive_user):
    """Создает токен для неактивного пользователя"""
    return create_access_token(subject=inactive_user.id)
