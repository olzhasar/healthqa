from flask import Flask, g
from flask_wtf import CSRFProtect

from account.views import bp as account_bp
from app import commands, context_processors, error_handlers, filters
from app.config import settings
from app.login import login_manager
from auth.views import bp as auth_bp
from home.views import bp as home_bp
from questions.views import bp as questions_bp
from users.views import bp as users_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(settings.TEMPLATES_DIR),
        static_folder=str(settings.STATIC_DIR),
        static_url_path="/static",
    )

    app.config.from_object(settings)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(account_bp)

    CSRFProtect(app)

    @app.teardown_appcontext  # type:ignore
    def teardown(exception: Exception) -> None:
        store = getattr(g, "_store", None)
        if store is not None:
            store.teardown()

    login_manager.init_app(app)
    context_processors.init_app(app)
    filters.init_app(app)
    commands.init_app(app)
    error_handlers.init_app(app)

    return app
