from datetime import datetime

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime


class TimeStamped:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
