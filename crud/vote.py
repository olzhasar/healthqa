from collections import defaultdict

from sqlalchemy.orm.session import Session

from models.vote import Vote


def get_dict_for_user(db: Session, user_id: int):
    result = defaultdict(lambda: 0)

    votes = (
        db.query(Vote.user_action_id, Vote.value).filter(Vote.user_id == user_id).all()
    )

    for action_id, value in votes:
        result[action_id] = value

    return result
