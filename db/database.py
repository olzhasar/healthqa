from typing import cast

from flask import g
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from werkzeug.local import LocalProxy

from app.config import settings
from db.engine import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = getattr(g, "_database", None)
    if db is None:
        if settings.TESTING:
            from tests.common import TestSession

            g._database = TestSession
        else:
            g._database = scoped_session(SessionLocal)
    return g._database


_db = LocalProxy(get_db)
db = cast(Session, _db)
