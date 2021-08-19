import os
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from app.config import settings
from mail.sender import send_templated_email


@pytest.fixture
def mock_send_mail(mocker: MockerFixture):
    return mocker.patch("mail.sender.send_mail")


@pytest.fixture
def template_file():
    file_path = os.path.join(settings.EMAIL_TEMPLATES_DIR, "test_template.txt")
    with open(file_path, "w") as f:
        f.write("Hello, {{ name }}. Your email is {{ email }}")

    yield

    os.remove(file_path)


def test_send_templated_email(mock_send_mail: MagicMock, template_file):
    to_email = "info@example.com"
    subject = "Test subject"
    expected_message = "Hello, User. Your email is info@example.com"

    send_templated_email(
        to=to_email,
        subject=subject,
        template="test_template",  # type: ignore
        context={"name": "User", "email": to_email},
    )

    mock_send_mail.assert_called_once_with(
        to=to_email, subject=subject, message=expected_message
    )
