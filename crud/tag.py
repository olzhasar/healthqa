from sqlalchemy.orm.session import Session

from models.tag import Tag


def get_all(db: Session, limit: int = 100):
    return db.query(Tag).limit(limit).all()
