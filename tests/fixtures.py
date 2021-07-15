from typing import Generator

import pytest
from sqlalchemy_utils import create_database, database_exists

import models
from app.main import app
from db.database import engine
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
    session = TestSession()
    try:
        yield session
    finally:
        session.rollback()
        TestSession.remove()


@pytest.fixture(scope="module")
def client():
    with app.test_client() as client:
        yield client
