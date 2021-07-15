from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db.dsn import POSTGRES_DSN

engine = create_engine(POSTGRES_DSN, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(SessionLocal)
