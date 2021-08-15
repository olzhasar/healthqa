from sqlalchemy.orm.session import Session

from models.tag import Tag


def get_list(db: Session):
    return db.query(Tag).all()


def get_choices(db: Session):
    return db.query(Tag.id, Tag.name).all()
