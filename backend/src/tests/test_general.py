from db.dsn import get_dsn


def test_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test_secret_key"
    assert app.config["BCRYPT_ROUNDS"] == 6

    DSN = get_dsn()
    assert DSN.endswith("_test")
