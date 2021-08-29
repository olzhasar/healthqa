import pytest

from app.config import settings
from db import database
from tests.session import TestSession


@pytest.fixture(autouse=True)
def set_variables(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "SECRET_KEY", "test_secret_key")
    monkeypatch.setattr(settings, "TESTING", True)
    monkeypatch.setattr(settings, "BCRYPT_ROUNDS", 6)
    monkeypatch.setattr(settings, "WTF_CSRF_ENABLED", False)
    monkeypatch.setattr(settings, "DB_NAME", "healthqa_test")

    monkeypatch.setattr(database, "get_session", lambda: TestSession)


pytest_plugins = [
    "tests.fixtures",
    "tests.db_fixtures",
    "tests.factory_fixtures",
]
