# tests/test_core/test_database.py
from sqlalchemy.orm import Session

from app.core.database import engine, SessionLocal, get_db

def test_engine_creation():
    """Тест создания движка SQLAlchemy"""
    # Проверка, что engine инициализирован правильно
    assert engine is not None

def test_session_local():
    """Тест создания сессии SQLAlchemy"""
    # Создание тестовой сессии
    session = SessionLocal()

    # Проверка типа сессии
    assert isinstance(session, Session)

    # Закрытие сессии
    session.close()

def test_get_db():
    """Тест генератора БД"""
    # Получение генератора
    db_gen = get_db()

    # Получение сессии из генератора
    db = next(db_gen)

    # Проверка типа сессии
    assert isinstance(db, Session)

    # Закрытие сессии
    try:
        next(db_gen)
    except StopIteration:
        pass
