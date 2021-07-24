import logging

from app.factory import create_app

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app = create_app()
