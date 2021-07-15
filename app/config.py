from pydantic import BaseSettings


class Settings(BaseSettings):
    TESTING = False

    DB_NAME: str = "healthqa"
    DB_USER: str = "healthqa"
    DB_PASSWORD: str = "healthqa"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    EXPLAIN_TEMPLATE_LOADING = False


settings = Settings()
