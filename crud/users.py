from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.security import hash_password
from models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def email_exists(db: Session, email: str) -> bool:
    return bool(db.query(User.id).filter(User.email == email).first())


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def username_exists(db: Session, username: str) -> bool:
    return bool(db.query(User.id).filter(User.username == username).first())


def get_by_username_or_email(db: Session, value: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(
            or_(
                User.username == value,
                User.email == value,
            )
        )
        .first()
    )


def create_user(db: Session, username: str, email: str, password: str) -> User:
    user = User(
        username=username,
        email=email,
        password=hash_password(password),
    )

    db.add(user)
    db.commit()

    return user


def username_or_email_taken(db: Session, username: str, email: str):
    return bool(
        db.query(User.id)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
