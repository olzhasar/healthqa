from contextlib import contextmanager
from typing import Any, Generator

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

import models
from app.factory import create_app
from app.login import login_manager
from db.engine import engine
from tests.common import TestSession


@pytest.fixture(scope="session", autouse=True)
def _prepare_db():
    engine.echo = True

    if not database_exists(engine.url):
        create_database(engine.url)

    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    TestSession.configure(bind=engine)


@pytest.fixture
def db() -> Generator:
    with TestSession() as session:
        session.begin_nested()
        yield session
        session.rollback()

    TestSession.remove()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@contextmanager
def authenticate(user, db):
    @login_manager.request_loader
    def load_user_from_request(request):
        db.refresh(user)
        return user

    yield user

    login_manager._request_callback = None


@pytest.fixture
def as_user(user, db, client):
    with authenticate(user, db):
        yield client


class QueriesCounter:
    def __init__(self, db: Session):
        self._count: int = 0
        self._do_count: bool = False
        self.queries: list[tuple[Any, ...]] = []
        event.listen(db.bind, "after_cursor_execute", self.callback)

    def __enter__(self):
        self._do_count = True
        return self

    def __exit__(self, type, value, traceback):
        self._do_count = False

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        if self._do_count:
            self._count += 1
            self.queries.append((statement, parameters, context))

    def __len__(self) -> int:
        return self._count


@pytest.fixture
def queries_counter(db):
    return QueriesCounter(db)
