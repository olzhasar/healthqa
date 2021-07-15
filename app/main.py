from pathlib import Path

from flask import Flask

from app.config import settings
from views.home import bp as home_bp

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES_DIR = BASE_DIR.joinpath("templates")


def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR)
    app.config.from_object(settings)

    app.register_blueprint(home_bp)

    return app
