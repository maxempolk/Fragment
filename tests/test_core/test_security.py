# tests/test_core/test_security.py
from jose import jwt
from datetime import timedelta

from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings

def test_create_access_token():
    """Тест создания JWT токена доступа"""
    # Подготовка тестовых данных
    user_id = 1
    expires = timedelta(minutes=15)

    # Вызов тестируемой функции
    token = create_access_token(subject=user_id, expires_delta=expires)

    # Проверка результата
    assert token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(user_id)
    assert "exp" in payload

def test_verify_password():
    """Тест проверки пароля"""
    # Подготовка тестовых данных
    plain_password = "testpassword123"
    hashed_password = get_password_hash(plain_password)

    # Вызов тестируемой функции и проверка результата
    assert verify_password(plain_password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)

def test_get_password_hash():
    """Тест хеширования пароля"""
    # Подготовка тестовых данных
    password = "testpassword123"

    # Вызов тестируемой функции
    hashed_password = get_password_hash(password)

    # Проверка результата
    assert hashed_password
    assert password not in hashed_password  # Хеш не должен содержать исходный пароль
    assert get_password_hash(password) != get_password_hash(password)  # Каждый хеш должен быть уникальным (соль)
