from flask import Flask, g, render_template
from flask_wtf import CSRFProtect

from app import commands, context_processors
from app.config import settings
from app.login import login_manager
from auth.views import bp as auth_bp
from home.views import bp as home_bp
from questions.views import bp as questions_bp
from users.views import bp as users_bp


def create_app() -> Flask:
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

    @app.errorhandler(404)
    def error_404(e):
        return render_template("404.html")

    @app.errorhandler(500)
    def error_500(e):
        return render_template("500.html")

    login_manager.init_app(app)
    commands.init_app(app)
    context_processors.init_app(app)

    return app
