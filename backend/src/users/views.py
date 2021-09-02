from flask import Blueprint, abort, render_template
from flask.globals import request

import crud
from repository.exceptions import NotFoundError
from repository.user import UserRepository
from storage import store

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
def all():
    page = int(request.args.get("page", 1))

    repo = UserRepository(store)
    paginator = repo.list(page=page, per_page=16)

    return render_template("users/list.html", paginator=paginator)


@bp.route("/<int:id>/")
def profile(id: int):
    repo = UserRepository(store)
    try:
        user = repo.get(id)
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
