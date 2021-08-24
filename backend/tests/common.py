from sqlalchemy.orm import scoped_session, sessionmaker

TestSession = scoped_session(sessionmaker())
