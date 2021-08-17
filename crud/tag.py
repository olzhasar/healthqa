from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from models.tag import Tag, TagCategory


def get_by_slug(db: Session, slug: str) -> Tag:
    return db.query(Tag).filter(Tag.slug == slug).one()


def get_list(db: Session) -> list[Tag]:
    return db.query(Tag).all()


def get_choices(db: Session) -> list[tuple[int, str]]:
    return db.query(Tag.id, Tag.name).all()


def get_categories_list(db: Session) -> list[TagCategory]:
    return db.query(TagCategory).options(joinedload(TagCategory.tags)).all()
