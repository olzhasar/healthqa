import logging
import os
from contextlib import contextmanager
from typing import Any, Generator

import pytest
from flask import Flask
from flask import template_rendered as flask_template_rendered
from redis import Redis
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from app.config import settings
from app.factory import create_app
from app.login import login_manager
from db.engine import engine
from tests.session import TestSession

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


@pytest.fixture(scope="session", autouse=True)
def _redis_db():
    yield Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=15)


@pytest.fixture
def redis_db(_redis_db):
    yield _redis_db
    _redis_db.flushdb()


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
def with_app_context(app: Flask):
    with app.app_context():
        yield


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
            if not statement.startswith(("SAVEPOINT", "RELEASE")):
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
            yield c
            if len(c) > num_queries:
                logger.error("Captured queries:\n")
                for query in c.queries:
                    logger.error(f"{query[0]}\n")

                raise AssertionError(
                    f"Expected {num_queries} queries, but {len(c)} were performed"
                )

    return _max_num_queries


@pytest.fixture
def captured_templates(app):
    recorded = set()

    def record(sender, template, context, **extra):
        recorded.add(template.name)

    flask_template_rendered.connect(record, app)
    yield recorded
    flask_template_rendered.disconnect(record, app)


@pytest.fixture
def template_rendered(captured_templates):
    def _template_rendered(template_name: str):
        return template_name in captured_templates

    return _template_rendered
