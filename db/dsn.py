from pydantic import PostgresDsn

from app.config import settings

DB_PATH = f"/{settings.DB_NAME}"
if settings.TESTING:
    DB_PATH += "_test"

POSTGRES_DSN = PostgresDsn.build(
    scheme="postgresql",
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    path=DB_PATH,
)
