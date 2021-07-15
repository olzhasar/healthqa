from app.main import app
from db.dsn import POSTGRES_DSN


def test_config():
    assert app.config["TESTING"] is True
    assert POSTGRES_DSN.endswith("_test")
