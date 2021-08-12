from typing import Optional

from sqlalchemy.orm import Session, with_expression
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import func

from app.security import hash_password
from models.entry import Entry
from models.user import User


def get(db: Session, *, id: int) -> User:
    return db.query(User).filter(User.id == id).one()


def get_by_email(db: Session, *, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def email_exists(db: Session, *, email: str) -> bool:
    return bool(db.query(User.id).filter(User.email == email).first())


def for_list(db: Session, *, limit: int = 30, offset: int = 0) -> list[User]:
    question_count = (
        select(func.count(Entry.id))
        .where(and_(Entry.user_id == User.id, Entry.type == 1))
        .scalar_subquery()
    )
    answer_count = (
        select(func.count(Entry.id))
        .where(and_(Entry.user_id == User.id, Entry.type == 2))
        .scalar_subquery()
    )
    comment_count = (
        select(func.count(Entry.id))
        .where(and_(Entry.user_id == User.id, Entry.type == 3))
        .scalar_subquery()
    )

    return (
        db.query(User)
        .options(
            with_expression(User.question_count, question_count),
            with_expression(User.answer_count, answer_count),
            with_expression(User.comment_count, comment_count),
        )
        .limit(limit)
        .offset(offset)
        .all()
    )


def count(db: Session) -> int:
    return db.query(func.count(User.id)).scalar()


def create_user(db: Session, *, email: str, name: str, password: str) -> User:
    user = User(
        email=email,
        name=name,
        password=hash_password(password),
    )

    db.add(user)
    db.commit()

    return user
