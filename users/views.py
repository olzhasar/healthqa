from flask import Blueprint, abort, render_template
from flask.globals import request
from sqlalchemy.exc import NoResultFound

import crud
from common.pagination import Paginator
from db.database import db

bp = Blueprint("users", __name__, template_folder="templates", url_prefix="/users")


@bp.route("/")
def all():
    paginator = Paginator(
        total=crud.user.count(db),
        current=request.args.get("page", 1),
        per_page=30,
    )

    users = crud.user.for_list(db, limit=paginator.limit, offset=paginator.offset)

    return render_template("user_list.html", users=users, paginator=paginator)


@bp.route("/<int:id>/")
def profile(id: int):
    try:
        user = crud.user.get(db, id=id)
    except NoResultFound:
        abort(404)

    return render_template("profile.html", user=user)
