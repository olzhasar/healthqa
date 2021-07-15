import os

os.environ["TESTING"] = "1"
os.environ["BCRYPT_ROUNDS"] = "6"

pytest_plugins = [
    "tests.factory_fixtures",
]
