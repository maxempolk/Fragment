# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import router as api_router
from app.core.database import engine
from app.core.database import Base
import app.models  # Импортируем все модели для создания таблиц

# Создание экземпляра приложения FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Настройка CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Подключение API роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)

# Создание таблиц базы данных при запуске (для разработки)
# В продакшене лучше использовать Alembic для миграций
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Добро пожаловать в API сервиса хранения фрагментов кода!"}
