from sqlalchemy.orm.session import Session

from models.question import Question


def get_all(db: Session, limit: int = 10):
    return db.query(Question).limit(limit).all()
