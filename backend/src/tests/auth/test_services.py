from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm.session import Session

from auth import security
from auth.services import (
    generate_and_send_password_reset_link,
    generate_and_send_verification_link,
)
from mail.sender import send_templated_email
from mail.template import EmailTemplate
from tests.utils import full_url_for


@pytest.mark.freeze_time("2020-01-01")
def test_generate_and_send_verification_link(
    with_app_context, db: Session, user, mock_enqueue: MagicMock
):
    token = security.make_url_safe_token(user.id)
    url = full_url_for("auth.verify_email", token=token)

    generate_and_send_verification_link(user)

    context = dict(
        name=user.name,
        url=url,
    )
    kwargs = dict(
        to=user.email,
        subject="Account activation",
        template=EmailTemplate.VERIFY_EMAIL,
        context=context,
    )
    mock_enqueue.assert_called_once_with(send_templated_email, **kwargs)


@pytest.mark.freeze_time("2020-01-01")
def test_generate_and_send_password_reset_link(
    with_app_context, db: Session, user, mock_enqueue: MagicMock
):
    token = security.make_url_safe_token(user.id)
    url = full_url_for("auth.reset_password", token=token)

    generate_and_send_password_reset_link(user)

    context = dict(
        name=user.name,
        url=url,
    )
    kwargs = dict(
        to=user.email,
        subject="Password reset",
        template=EmailTemplate.RESET_PASSWORD,
        context=context,
    )
    mock_enqueue.assert_called_once_with(send_templated_email, **kwargs)
