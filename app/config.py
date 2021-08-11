from pydantic import BaseSettings


class Settings(BaseSettings):
    TESTING = False

    SECRET_KEY: str = "supersecretkey"

    DB_NAME: str = "healthqa"
    DB_USER: str = "healthqa"
    DB_PASSWORD: str = "healthqa"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    SQLALCHEMY_LOGGING_LEVEL: str = "WARNING"

    EXPLAIN_TEMPLATE_LOADING: bool = False

    BCRYPT_ROUNDS: int = 12
    WTF_CSRF_ENABLED: bool = True

    PAGINATION: int = 20


settings = Settings()
