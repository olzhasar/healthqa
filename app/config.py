from pydantic import BaseSettings


class Settings(BaseSettings):
    TESTING = False

    SECRET_KEY: str = "supersecretkey"

    DB_NAME: str = "healthqa"
    DB_USER: str = "healthqa"
    DB_PASSWORD: str = "healthqa"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    EXPLAIN_TEMPLATE_LOADING = False

    BCRYPT_ROUNDS = 12


settings = Settings()
