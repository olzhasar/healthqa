from flask_login import LoginManager
from sqlalchemy.orm import undefer

from models.user import User
from repository.exceptions import NotFoundError
from repository.user import UserRepository
from storage import store

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str):
    repo = UserRepository(store)
    try:
        return repo.get(int(user_id))
    except NotFoundError:
        return None
