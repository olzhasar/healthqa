from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pydantic import PostgresDsn
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.config import settings

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine


def get_dsn() -> str:
    return PostgresDsn.build(
        scheme="postgresql",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        path=f"/{settings.DB_NAME}",
    )


def create_engine() -> Engine:
    return sqlalchemy_create_engine(get_dsn(), pool_pre_ping=True)


def create_session() -> Session:
    engine = create_engine()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = scoped_session(SessionLocal)
    return cast(Session, session)
