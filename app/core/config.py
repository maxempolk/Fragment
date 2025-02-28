from pydantic import MySQLDsn, field_validator, ValidationInfo, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Общие настройки
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "Code Snippets Repository"

    # Настройки базы данных
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before") # pyright: ignore
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str | Optional[MySQLDsn]:
        if v is not None:
            return v

        values = info.data

        user = values.get("MYSQL_USER")
        password = values.get("MYSQL_PASSWORD")
        server = values.get("MYSQL_SERVER")
        db = values.get("MYSQL_DB")

        # Проверка, что все необходимые компоненты URL присутствуют
        if not all([user, password, server]):
            raise ValueError("Missing required components for database URL")

        # Построение URL с путем базы данных, только если он существует
        path = f"{db}" if db else ""

        return str(MySQLDsn.build(
            scheme="mysql+pymysql",
            username=user,
            password=password,
            host=server, # pyright: ignore
            path=path,
        ))

    # Настройки JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 минут
    ALGORITHM: str = "HS256"

    # Настройки CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://localhost:3000"]

    model_config = ConfigDict(env_file = ".env", case_sensitive = True) # pyright: ignore


settings = Settings(
    MYSQL_SERVER = "localhost",
    MYSQL_USER = "root",
    MYSQL_PASSWORD = "1234",
    MYSQL_DB = "FRAGMENT",
)
