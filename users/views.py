from flask import Blueprint, abort, render_template
from sqlalchemy.exc import NoResultFound

import crud
from db.database import db

bp = Blueprint("users", __name__, template_folder="templates", url_prefix="/users")


@bp.route("/")
def all():
    return render_template("user_list.html")


@bp.route("/<int:id>/")
def profile(id: int):
    try:
        user = crud.user.get(db, id=id)
    except NoResultFound:
        abort(404)

    return render_template("profile.html", user=user)
