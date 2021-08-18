from flask import Flask, g
from flask_wtf import CSRFProtect

from app import commands, context_processors
from app.config import settings
from app.login import login_manager
from auth.views import bp as auth_bp
from home.views import bp as home_bp
from questions.views import bp as questions_bp
from users.views import bp as users_bp


def create_app():
    app = Flask(
        __name__,
        template_folder=settings.TEMPLATES_DIR,
        static_folder=settings.STATIC_DIR,
        static_url_path="/static",
    )
    app.config.from_object(settings)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)

    CSRFProtect(app)

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()

    login_manager.init_app(app)
    commands.init_app(app)
    context_processors.init_app(app)

    return app
