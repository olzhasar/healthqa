import smtplib
import ssl

from app.config import settings


def send_mail(to_email: str, subject: str, message: str) -> None:
    from_email = settings.EMAIL_USER
    content = f"From: {from_email}\nTo: {to_email}\nSubject: {subject}\n\n{message}"

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        host=settings.EMAIL_HOST, port=settings.EMAIL_PORT, context=context
    ) as server:
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_USER, to_email, content)
