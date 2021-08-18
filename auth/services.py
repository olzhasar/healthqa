from flask import url_for

from auth import security
from mail.sender import send_templated_email
from mail.template import EmailTemplate
from models.user import User
from worker import queue


def generate_and_send_verification_link(user: User):
    token = security.make_url_safe_token(user.id)
    url = url_for("auth.verify_email", token=token, _external=True)
    email_context = dict(name=user.name, url=url)

    queue.enqueue(
        send_templated_email,
        to=user.email,
        subject="Account activation",
        template=EmailTemplate.VERIFY_EMAIL,
        context=email_context,
    )
