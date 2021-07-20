from flask import Blueprint, abort, redirect, render_template, url_for
from flask_login import current_user, login_required

import crud
from db.database import db
from questions.forms import AskQuestionForm

bp = Blueprint(
    "questions", __name__, template_folder="templates", url_prefix="/questions"
)


@bp.route("/<int:id>")
def details(id: int):
    question = crud.question.get_by_id(db, id)
    if not question:
        abort(404)

    return render_template("details.html", question=question)


@bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask():
    form = AskQuestionForm()
    if form.validate_on_submit():
        crud.question.create(
            db,
            user=current_user,
            title=form.title.data,
            content=form.content.data,
            tags=[],
        )
        return redirect(url_for("home.index"))
    return render_template("ask_question.html", form=form)
