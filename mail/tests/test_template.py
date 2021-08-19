import os

from app.config import settings
from mail.template import EmailTemplate


def test_email_templates_exist():
    for choice in EmailTemplate:
        file_path = os.path.join(settings.EMAIL_TEMPLATES_DIR, f"{choice.value}.txt")
        assert os.path.exists(file_path)
