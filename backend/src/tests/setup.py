import os

import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from tests.session import TestSession


@pytest.fixture(scope="session", autouse=True)
def _patch_session():
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("db.database.get_session", lambda: TestSession)

        yield


@pytest.fixture(scope="session", autouse=True)
def _prepare_db(_patch_session):
    from db.engine import engine

    if database_exists(engine.url):
        drop_database(engine.url)

    create_database(engine.url)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
    alembic_upgrade(alembic_cfg, "head")

    TestSession.configure(bind=engine)
