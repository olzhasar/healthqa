from typing import Optional, cast

import bcrypt
from itsdangerous.exc import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer

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


def make_url_safe_token(user_id: int) -> str:
    signer = URLSafeTimedSerializer(settings.SECRET_KEY)
    result = cast(str, signer.dumps(user_id))
    return result


def get_user_id_from_token(token: str, max_age: int) -> Optional[int]:
    signer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        return signer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        raise ValueError("Invalid token")
