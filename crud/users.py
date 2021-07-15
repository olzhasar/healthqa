from typing import Optional

from sqlalchemy.orm import Session

from app.security import hash_password
from models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, email: str, password: str) -> User:
    user = User(
        username=username,
        email=email,
        password=hash_password(password),
    )

    db.add(user)
    db.commit()

    return user
