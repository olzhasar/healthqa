from pathlib import Path

from flask import Flask, g

from app import commands
from app.config import settings
from app.login import login_manager
from auth.views import bp as auth_bp
from home.views import bp as home_bp

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES_DIR = BASE_DIR.joinpath("templates")
STATIC_DIR = BASE_DIR.joinpath("static")


def create_app():
    app = Flask(
        __name__,
        template_folder=TEMPLATES_DIR,
        static_folder=STATIC_DIR,
        static_url_path="/static",
    )
    app.config.from_object(settings)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()

    login_manager.init_app(app)
    commands.init_app(app)

    return app
