from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Создание URL подключения к базе данных
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Создание движка SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, # pyright: ignore
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
