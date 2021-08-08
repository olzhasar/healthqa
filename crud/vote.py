from collections import defaultdict

from sqlalchemy.orm.session import Session

from models.user import User
from models.vote import Vote


def get(db: Session, *, user_id: int, entry_id: int):
    return db.query(Vote).filter(Vote.user_id == user_id, entry_id == entry_id).first()


def get_dict_for_user(db: Session, *, user_id: int):
    result = defaultdict(lambda: 0)

    votes = db.query(Vote.entry_id, Vote.value).filter(Vote.user_id == user_id).all()

    for action_id, value in votes:
        result[action_id] = value

    return result


def delete_by_user_id_user_action_id(db: Session, *, user_id: int, entry_id: int):
    db.query(Vote).filter(Vote.user_id == user_id, Vote.entry_id == entry_id).delete()
    db.commit()


def create(db: Session, *, user: User, entry_id: int, value: int):
    vote = Vote(user=user, entry_id=entry_id, value=value)

    db.add(vote)
    db.commit()

    return vote
