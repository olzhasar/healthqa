import os
from typing import Generator

import pytest
from sqlalchemy.engine.base import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from tests.session import TestSession


@pytest.fixture(scope="session")
def engine() -> Engine:
    from storage.db import create_engine

    return create_engine()


@pytest.fixture(scope="session")
def connection(engine: Engine) -> Generator:
    _connection = engine.connect()
    try:
        yield _connection
    finally:
        _connection.close()


@pytest.fixture(scope="session")
def _setup_db(engine):
    if database_exists(engine.url):
        drop_database(engine.url)

    create_database(engine.url)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
    alembic_upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def _patch_create_session():
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("storage.base.create_session", lambda: TestSession)

        yield


class StoreBlocker:
    def __init__(self):
        self._real_db = self._store_wrapper.db
        self._real_redis = self._store_wrapper.redis

    @property
    def _store_wrapper(self):
        from storage.base import Store

        return Store

    def forbid_db(self, store):
        raise RuntimeError("Database access is not allowed")

    def forbid_redis(self, store):
        raise RuntimeError("Redis access is not allowed")

    def block_db(self):
        self._store_wrapper.db = property(self.forbid_db)

    def block_redis(self):
        self._store_wrapper.redis = property(self.forbid_redis)

    def unblock_db(self):
        self._store_wrapper.db = self._real_db

    def unblock_redis(self):
        self._store_wrapper.redis = self._real_redis


@pytest.fixture(scope="session")
def _store_blocker():
    return StoreBlocker()


@pytest.fixture(scope="session", autouse=True)
def _block_db(_store_blocker):
    _store_blocker.block_db()


@pytest.fixture(scope="session", autouse=True)
def _block_redis(_store_blocker):
    _store_blocker.block_redis()


@pytest.fixture()
def _unblock_db(_store_blocker, db):
    _store_blocker.unblock_db()
    yield
    _store_blocker.block_db()


@pytest.fixture()
def _unblock_redis(_store_blocker, redis_db):
    _store_blocker.unblock_redis()
    yield
    _store_blocker.block_redis()


@pytest.fixture(autouse=True)
def _allow_markers(request):
    markers = {
        "allow_db": "_unblock_db",
        "allow_redis": "_unblock_redis",
    }

    for marker_name, fixture_name in markers.items():
        marker = request.node.get_closest_marker(marker_name)
        if marker:
            request.getfixturevalue(fixture_name)
