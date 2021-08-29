from typing import cast

from flask import g
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from werkzeug.local import LocalProxy

from db.engine import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return scoped_session(SessionLocal)


def get_db() -> Session:
    db = getattr(g, "_database", None)
    if db is None:
        g._database = get_session()
    return g._database


_db = LocalProxy(get_db)
db = cast(Session, _db)
