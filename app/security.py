import bcrypt

from app.config import settings


def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(
        raw_password.encode("utf-8"),
        bcrypt.gensalt(settings.BCRYPT_ROUNDS),
    ).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8"),
    )
