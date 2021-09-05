from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    TESTING: bool = False

    SECRET_KEY: str

    SERVER_NAME: str = "localhost:5000"

    DB_NAME: str = "healthqa"
    DB_USER: str = "healthqa"
    DB_PASSWORD: str = "healthqa"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    SQLALCHEMY_LOGGING_LEVEL: str = "DEBUG"

    EXPLAIN_TEMPLATE_LOADING: bool = False

    BCRYPT_ROUNDS: int = 12
    WTF_CSRF_ENABLED: bool = True

    PAGINATION: int = 20

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_RQ_DB: int = 0
    REDIS_MAIN_DB: int = 1

    EMAIL_HOST: str = "smtp.yandex.com"
    EMAIL_PORT: int = 465
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""

    TOKEN_MAX_AGE_EMAIL_VERIFICATION = 3600 * 24 * 7
    TOKEN_MAX_AGE_PASSWORD_RESET = 3600 * 3

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
    TEMPLATES_DIR = BASE_DIR.joinpath("templates")
    EMAIL_TEMPLATES_DIR = BASE_DIR.joinpath("email_templates")
    FRONTEND_DIR = BASE_DIR.parent.parent.joinpath("frontend")
    STATIC_DIR = FRONTEND_DIR.joinpath("dist")

    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.3

    class Config:
        env_file = ".env"


settings = Settings()
