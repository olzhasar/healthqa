from flask_login import LoginManager

from db.database import db
from models.user import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str):
    return db.query(User).filter(User.id == int(user_id)).first()
