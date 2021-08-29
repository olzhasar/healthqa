from sqlalchemy import create_engine

from db.dsn import get_dsn

engine = create_engine(get_dsn(), pool_pre_ping=True)
