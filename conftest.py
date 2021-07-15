import os

os.environ["TESTING"] = "1"
os.environ["BCRYPT_ROUNDS"] = "6"
os.environ["WTF_CSRF_ENABLED"] = "0"

pytest_plugins = [
    "tests.fixtures",
    "tests.factory_fixtures",
]
