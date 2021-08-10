from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError, NoResultFound

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
    try:
        question = crud.question.get_for_view(db, id)
    except NoResultFound:
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


@bp.route("/entries/<int:id>/comment", methods=["POST"])
@login_required
def comment(id: int):
    form = forms.CommentForm()

    if form.validate_on_submit():
        try:
            comment = crud.comment.create(
                db,
                user=current_user,
                entry_id=id,
                content=form.content.data,
            )
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "invalid entry_id"}), 400
        else:
            return render_template("_comment.html", comment=comment)

    return render_template(
        "_comment_form.html",
        comment_form=form,
        url=request.url,
    )


@bp.route("/entries/<int:id>/vote/<int:value>", methods=["POST"])
@login_required
def vote(id: int, value: int):
    """
    value 1 - upvote
    value 2 - downvote
    """

    if not crud.entry.exists(db, id=id):
        return jsonify({"error": "invalid entry_id"}), 404

    existing = crud.vote.one_or_none(db, user_id=current_user.id, entry_id=id)

    if value == 0:
        if existing:
            db.delete(existing)
            db.commit()
        else:
            return jsonify({"error": "Vote does not exist"}), 400

    elif value in [1, 2]:
        if value == 2:
            value = -1

        if existing:
            if existing.value == value:
                return jsonify({"error": "Vote already exists"}), 400

            existing.value = value
            db.add(existing)
            db.commit()
        else:
            crud.vote.create(
                db,
                user_id=current_user.id,
                entry_id=id,
                value=value,
            )
    else:
        return jsonify({"error": "Invalid vote value"}), 400

    entry = crud.entry.get(db, id=id)
    if entry.type == 3:
        template_name = "_vote_comment.html"
    else:
        template_name = "_vote_large.html"

    return render_template(template_name, entry=entry)
