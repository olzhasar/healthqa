from flask_login import LoginManager
from sqlalchemy.orm import undefer

from db.database import db
from models.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str):
    return (
        db.query(User)
        .options(undefer("password"))
        .filter(User.id == int(user_id))
        .first()
    )
