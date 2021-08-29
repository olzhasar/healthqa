import logging

from app.factory import create_app

logging.basicConfig()

app = create_app()

logging.getLogger("sqlalchemy.engine").setLevel(app.config["SQLALCHEMY_LOGGING_LEVEL"])
