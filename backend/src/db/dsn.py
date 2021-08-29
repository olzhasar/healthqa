from pydantic import PostgresDsn

from app.config import settings


def get_dsn():
    return PostgresDsn.build(
        scheme="postgresql",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        path=f"/{settings.DB_NAME}",
    )
