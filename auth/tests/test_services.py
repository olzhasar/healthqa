from unittest.mock import MagicMock

import pytest
from flask import url_for
from pytest_mock import MockerFixture
from sqlalchemy.orm.session import Session

from auth import security
from auth.services import generate_and_send_verification_link
from mail.sender import send_templated_email
from mail.template import EmailTemplate


@pytest.fixture
def mock_enqueue(mocker: MockerFixture):
    return mocker.patch("worker.queue.enqueue")


@pytest.mark.freeze_time("2020-01-01")
def test_generate_and_send_verification_link(
    with_app_context, db: Session, user, mock_enqueue: MagicMock
):
    token = security.make_url_safe_token(user.id)
    url = url_for("auth.verify_email", token=token, _external=True)

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
