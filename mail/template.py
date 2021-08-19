from enum import Enum, unique


@unique
class EmailTemplate(Enum):
    VERIFY_EMAIL = "verify_email"
    RESET_PASSWORD = "reset_password"
