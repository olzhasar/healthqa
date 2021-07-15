from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.dsn import POSTGRES_DSN

engine = create_engine(POSTGRES_DSN, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
