import os

os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["TESTING"] = "1"
os.environ["BCRYPT_ROUNDS"] = "6"
os.environ["WTF_CSRF_ENABLED"] = "0"
os.environ["DB_NAME"] = "healthqa_test"
os.environ["REDIS_MAIN_DB"] = "15"


pytest_plugins = [
    "tests.setup",
    "tests.fixtures",
    "tests.db_fixtures",
    "tests.factory_fixtures",
]
