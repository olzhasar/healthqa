from typing import Optional

from sqlalchemy.orm import Session

from app.security import hash_password
from models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def email_exists(db: Session, email: str) -> bool:
    return bool(db.query(User.id).filter(User.email == email).first())


def create_user(db: Session, email: str, password: str) -> User:
    user = User(
        email=email,
        password=hash_password(password),
    )

    db.add(user)
    db.commit()

    return user
