from sqlalchemy import Column, Integer, String

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(100))
    username = Column(String(50), unique=True)
