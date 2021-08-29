from flask import g

from db.database import db
from db.redis import redis_db
from tests.session import TestSession


def test_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test_secret_key"
    assert app.config["BCRYPT_ROUNDS"] == 6


def test_database_patched(with_app_context):
    db.query()
    assert g._database == TestSession
    assert db.bind.url.database.endswith("_test")


def test_redis_patched(with_app_context):
    assert redis_db.connection_pool.connection_kwargs["db"] == 15
