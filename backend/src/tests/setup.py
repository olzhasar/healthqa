import os

import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from tests.session import TestSession


@pytest.fixture(scope="session")
def _engine():
    from storage.db import create_engine

    return create_engine()


@pytest.fixture(scope="session")
def _prepare_db(_engine):
    if database_exists(_engine.url):
        drop_database(_engine.url)

    create_database(_engine.url)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
    alembic_upgrade(alembic_cfg, "head")

    TestSession.configure(bind=_engine)


@pytest.fixture(scope="session", autouse=True)
def _patch_create_session(_prepare_db):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("storage.base.create_session", lambda: TestSession)

        yield
