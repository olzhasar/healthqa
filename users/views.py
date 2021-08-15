from flask import Blueprint, abort, redirect, render_template, url_for
from flask.globals import request
from flask_login import current_user, login_required
from sqlalchemy.exc import NoResultFound

import crud
from common.pagination import Paginator
from db.database import db
from users import forms

bp = Blueprint("users", __name__, template_folder="templates", url_prefix="/users")


@bp.route("/")
def all():
    paginator = Paginator(
        total=crud.user.count(db),
        current=request.args.get("page", 1),
        per_page=16,
    )

    users = crud.user.for_list(db, limit=paginator.limit, offset=paginator.offset)

    return render_template("user_list.html", users=users, paginator=paginator)


@bp.route("/<int:id>/")
def profile(id: int):
    try:
        user = crud.user.get_with_counts(db, id=id)
    except NoResultFound:
        abort(404)

    tab = request.args.get("tab", "questions")

    if tab == "questions":
        questions = crud.question.list_for_user(db, user_id=user.id)
        answers = []
    else:
        questions = []
        answers = crud.answer.list_for_user(db, user_id=user.id)

    return render_template(
        "profile.html", user=user, questions=questions, answers=answers, tab=tab
    )


@bp.route("<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(id: int):
    if current_user.id != id:
        abort(404)

    form = forms.ProfileForm(obj=current_user)
    if form.validate_on_submit():
        crud.user.update(db, user_id=current_user.id, name=form.name.data)
        return redirect(url_for("users.profile", id=current_user.id))

    return render_template("edit_profile.html", form=form)
