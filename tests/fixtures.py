from typing import Generator

import pytest
from sqlalchemy_utils import create_database, database_exists

import models
from app.factory import create_app
from db.engine import engine
from tests.common import TestSession


@pytest.fixture(scope="session", autouse=True)
def _prepare_db():
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
