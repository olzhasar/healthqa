from flask import Blueprint, abort, render_template
from flask.globals import request

import crud
import repository as repo
from repository.exceptions import NotFoundError
from storage import store

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
def all():
    page = int(request.args.get("page", 1))

    paginator = repo.user.list(store, page=page, per_page=16)

    return render_template("users/list.html", paginator=paginator)


@bp.route("/<int:id>/")
def profile(id: int):
    try:
        user = repo.user.get(store, id)
    except NotFoundError:
        abort(404)

    tab = request.args.get("tab", "questions")

    if tab == "questions":
        questions = crud.question.get_list_for_user(store.db, user_id=user.id)
        answers = []
    else:
        questions = []
        answers = crud.answer.get_list_for_user(store.db, user_id=user.id)

    return render_template(
        "users/profile.html", user=user, questions=questions, answers=answers, tab=tab
    )
