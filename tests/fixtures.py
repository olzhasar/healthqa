import logging
import os
from contextlib import contextmanager
from typing import Any, Generator

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from app.factory import create_app
from app.login import login_manager
from db.engine import engine
from tests.common import TestSession

logger = logging.Logger(__name__)


@pytest.fixture(scope="session", autouse=True)
def _prepare_db():
    if database_exists(engine.url):
        drop_database(engine.url)

    create_database(engine.url)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
    alembic_upgrade(alembic_cfg, "head")

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


@pytest.fixture
def max_num_queries(db):
    @contextmanager
    def _max_num_queries(num_queries: int):
        queries_counter = QueriesCounter(db)
        with queries_counter as c:
            yield
            if len(c) > num_queries:
                logger.error("Captured queries:\n")
                for query in c.queries:
                    logger.error(f"{query[0]}\n")

                raise AssertionError(
                    f"Expected {num_queries} queries, but {len(c)} were performed"
                )

    return _max_num_queries
