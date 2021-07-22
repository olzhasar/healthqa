from flask import Blueprint, abort, jsonify, redirect, render_template, url_for
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
            return render_template("_answer.html", answer=answer)
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid question_id"}), 403

    return jsonify(form.errors), 403


@bp.route("/questions/<int:id>/comment", methods=["POST"])
@login_required
def question_comment(id: int):
    form = forms.CommentForm()
    if form.validate_on_submit():
        try:
            crud.comment.create_for_question(
                db,
                user=current_user,
                question_id=id,
                content=form.content.data,
            )
            return jsonify({"success": True}), 201
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid question_id"}), 400

    return jsonify(form.errors), 400


@bp.route("/answers/<int:id>/comment", methods=["POST"])
@login_required
def answer_comment(id: int):
    form = forms.CommentForm()
    if form.validate_on_submit():
        try:
            crud.comment.create_for_answer(
                db,
                user=current_user,
                answer_id=id,
                content=form.content.data,
            )
            return jsonify({"success": True}), 201
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid answer_id"}), 400

    return jsonify(form.errors), 400
