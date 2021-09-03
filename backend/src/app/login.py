from __future__ import annotations

from typing import TYPE_CHECKING

from flask_login import LoginManager

from repository.exceptions import NotFoundError
from repository.user import UserRepository

if TYPE_CHECKING:
    from models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    repo = UserRepository()
    try:
        return repo.get_with_password(int(user_id))
    except NotFoundError:
        return None
