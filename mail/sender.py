import smtplib
import ssl
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.config import settings
from mail.template import EmailTemplate


def send_mail(*, to: str, subject: str, message: str) -> None:
    from_email = settings.EMAIL_USER
    content = f"From: {from_email}\nTo: {to}\nSubject: {subject}\n\n{message}"

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        host=settings.EMAIL_HOST, port=settings.EMAIL_PORT, context=context
    ) as server:
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_USER, to, content)


def send_templated_email(
    *, to: str, subject: str, template: EmailTemplate, context: dict[str, Any]
):
    loader = FileSystemLoader(settings.EMAIL_TEMPLATES_DIR)
    env = Environment(loader=loader)

    txt_template = env.get_template(f"{template}.txt")
    message = txt_template.render(**context)

    return send_mail(to=to, subject=subject, message=message)
