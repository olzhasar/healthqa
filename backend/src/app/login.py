from __future__ import annotations

from typing import TYPE_CHECKING

from flask_login import LoginManager

import repository as repo
from storage import store

if TYPE_CHECKING:
    from models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> User:
    return repo.user.first_with_password(store, int(user_id))
