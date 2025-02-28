# tests/test_core/test_config.py
import pytest
from pydantic import ValidationError

from app.core.config import Settings

def test_settings_validation():
    """Тест валидации настроек"""
    # Тест с отсутствующими параметрами
    with pytest.raises(ValidationError):
        Settings(MYSQL_USER="test")  # pyright: ignore

    # Успешный тест с минимальными настройками
    settings = Settings(
        MYSQL_SERVER="localhost",
        MYSQL_USER="testuser",
        MYSQL_PASSWORD="testpass",
        MYSQL_DB="testdb"
    )

    print( settings )
    assert settings.DATABASE_URL == "mysql+pymysql://testuser:testpass@localhost:3306/testdb"

    # Тест с предоставленным URL
    settings = Settings(
        MYSQL_SERVER="localhost",
        MYSQL_USER="testuser",
        MYSQL_PASSWORD="testpass",
        MYSQL_DB="testdb",
        DATABASE_URL="custom_url"
    )
    assert settings.DATABASE_URL == "custom_url"
