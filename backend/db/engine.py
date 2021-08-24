from sqlalchemy import create_engine

from db.dsn import POSTGRES_DSN

engine = create_engine(POSTGRES_DSN, pool_pre_ping=True)
