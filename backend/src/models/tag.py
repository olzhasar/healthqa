from flask.helpers import url_for
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from models.base import Base


class TagCategory(Base):
    __tablename__ = "tag_categories"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False, unique=True)
    tags: list["Tag"] = relationship("Tag", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False, unique=True)
    slug: str = Column(String, nullable=False, unique=True)
    category_id: int = Column(Integer, ForeignKey("tag_categories.id"), index=True)
    category: TagCategory = relationship("TagCategory", back_populates="tags")

    @property
    def url(self) -> str:
        return url_for("questions.by_tag", slug=self.slug)
