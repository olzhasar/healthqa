from flask import Flask

from app.config import settings


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    return app
