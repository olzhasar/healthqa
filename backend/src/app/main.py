import logging

from app.factory import create_app

logging.basicConfig()

app = create_app()

if app.config["SENTRY_DSN"]:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"],
        integrations=[FlaskIntegration()],
        traces_sample_rate=app.config["SENTRY_TRACES_SAMPLE_RATE"],
    )


logging.getLogger("sqlalchemy.engine").setLevel(app.config["SQLALCHEMY_LOGGING_LEVEL"])
