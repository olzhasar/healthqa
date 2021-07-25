from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

import crud
from db.database import db
from questions import forms

bp = Blueprint("questions", __name__, template_folder="templates")


@bp.route("/questions/ask", methods=["GET", "POST"])
@login_required
def ask():
    form = forms.AskQuestionForm()
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


@bp.route("/questions/<int:id>")
def details(id: int):
    question = crud.question.get_by_id(db, id)
    if not question:
        abort(404)

    answer_form = forms.AnswerForm()
    comment_form = forms.CommentForm()

    return render_template(
        "details.html",
        question=question,
        answer_form=answer_form,
        comment_form=comment_form,
    )


@bp.route("/questions/<int:id>/answer", methods=["POST"])
@login_required
def answer(id: int):
    form = forms.AnswerForm()
    if form.validate_on_submit():
        try:
            answer = crud.answer.create(
                db,
                user=current_user,
                question_id=id,
                content=form.content.data,
            )
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid question_id"}), 403
        else:
            comment_form = forms.CommentForm()
            return render_template(
                "_answer.html",
                answer=answer,
                comment_form=comment_form,
            )

    return render_template("_answer_form.html", answer_form=form, url=request.url)


@bp.route("/user_actions/<int:id>/comment", methods=["POST"])
@login_required
def comment(id: int):
    form = forms.CommentForm()

    if form.validate_on_submit():
        try:
            comment = crud.comment.create(
                db,
                user=current_user,
                user_action_id=id,
                content=form.content.data,
            )
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid user_action_id"}), 400
        else:
            return render_template("_comment.html", comment=comment)

    return render_template(
        "_comment_form.html",
        comment_form=form,
        url=request.url,
    )
