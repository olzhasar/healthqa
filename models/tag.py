from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
