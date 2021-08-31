from flask import g

from storage import store
from tests.session import TestSession


def test_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test_secret_key"
    assert app.config["BCRYPT_ROUNDS"] == 6


def test_database_patched(with_app_context):
    store.db.query()
    assert g._store.db == TestSession
    assert g._store.db.bind.url.database.endswith("_test")
