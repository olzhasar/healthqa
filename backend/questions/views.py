from flask import Blueprint, abort, jsonify, redirect, render_template, request
from flask.globals import current_app
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError, NoResultFound

import crud
from common.pagination import Paginator
from db.database import db
from questions import forms

bp = Blueprint("questions", __name__)


@bp.route("/questions/ask", methods=["GET", "POST"])
@login_required
def ask():
    form = forms.AskQuestionForm()
    form.tags.choices = crud.tag.get_categories_list(db)

    if form.validate_on_submit():
        question = crud.question.create(
            db,
            user=current_user,
            title=form.title.data,
            content=form.content.data,
            tags=form.tags.data,
        )
        return redirect(question.url)

    return render_template("questions/ask_question.html", form=form)


@bp.route("/questions/")
def all():
    total = crud.question.count(db)
    paginator = Paginator(
        total=total,
        current=request.args.get("page", 1),
        per_page=current_app.config["PAGINATION"],
    )

    questions = crud.question.get_list(
        db, limit=paginator.limit, offset=paginator.offset
    )

    return render_template(
        "questions/list.html",
        questions=questions,
        paginator=paginator,
    )


@bp.route("/tags/")
def tags():
    return render_template("questions/tag_list.html")


@bp.route("/tags/<string:slug>/")
def by_tag(slug: str):
    try:
        tag = crud.tag.get_by_slug(db, slug=slug)
    except NoResultFound:
        abort(404)

    total = crud.question.count(db, tag=tag)
    paginator = Paginator(
        total=total,
        current=request.args.get("page", 1),
        per_page=current_app.config["PAGINATION"],
    )

    questions = crud.question.get_list(
        db, tag=tag, limit=paginator.limit, offset=paginator.offset
    )

    return render_template(
        "questions/list.html",
        page_title=f'Results for "{tag.name}"',
        questions=questions,
        paginator=paginator,
    )


@bp.route("/questions/search")
def search():
    query = request.args.get("q", "")

    total = crud.question.search_count(db, query=query)
    paginator = Paginator(
        total=total,
        current=request.args.get("page", 1),
        per_page=current_app.config["PAGINATION"],
    )

    questions = crud.question.search(
        db, query=query, limit=paginator.limit, offset=paginator.offset
    )

    return render_template(
        "questions/search_results.html",
        questions=questions,
        query=query,
        paginator=paginator,
    )


@bp.route("/questions/<int:id>")
def details(id: int):
    additional_params = {}
    if current_user.is_authenticated:
        additional_params["user_id"] = current_user.id
        crud.view.create(db, entry_id=id, user_id=current_user.id)

    try:
        question = crud.question.get_with_related(db, id=id, **additional_params)
    except NoResultFound:
        abort(404)

    answers = crud.answer.get_list_for_question(
        db, question_id=question.id, **additional_params
    )

    answer_form = forms.AnswerForm()
    comment_form = forms.CommentForm()

    return render_template(
        "questions/details.html",
        question=question,
        answers=answers,
        answer_form=answer_form,
        comment_form=comment_form,
    )


@bp.route("/questions/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_question(id: int):
    try:
        question = crud.question.get(db, id=id)
    except NoResultFound:
        abort(404)

    if question.user != current_user:
        abort(403)

    form = forms.AskQuestionForm(obj=question)
    form.tags.choices = crud.tag.get_categories_list(db)

    if form.validate_on_submit():
        crud.question.update(
            db,
            question=question,
            new_title=form.title.data,
            new_content=form.content.data,
            tags=form.tags.data,
        )
        return redirect(question.url)

    return render_template("questions/question_edit.html", form=form)


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
                "questions/_answer.html",
                answer=answer,
                comment_form=comment_form,
            )

    return render_template(
        "questions/_answer_form.html", answer_form=form, url=request.url
    )


@bp.route("/answers/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_answer(id: int):
    try:
        answer = crud.answer.get(db, id=id)
    except NoResultFound:
        abort(404)

    if answer.user != current_user:
        abort(403)

    form = forms.AnswerForm(obj=answer)
    if form.validate_on_submit():
        crud.answer.update(db, answer=answer, new_content=form.content.data)
        return redirect(answer.url)

    return render_template("questions/answer_edit.html", form=form)


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
            return render_template("questions/_comment.html", comment=comment)

    return render_template(
        "questions/_comment_form.html",
        comment_form=form,
        url=request.url,
    )


@bp.route("/comments/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(id: int):
    try:
        comment = crud.comment.get_for_user(db, id=id, user_id=current_user.id)
    except NoResultFound:
        abort(404)

    form = forms.CommentForm(obj=comment)
    if form.validate_on_submit():
        crud.comment.update(db, instance=comment, content=form.content.data)
        return render_template("questions/_comment.html", comment=comment)

    return render_template("questions/_comment_edit.html", form=form, comment=comment)


@bp.route("/entries/<int:id>/vote/<int:value>", methods=["POST"])
@login_required
def vote(id: int, value: int):
    """
    value 1 - upvote
    value 2 - downvote
    """

    if not crud.entry.exists(db, id=id):
        return jsonify({"error": "invalid entry_id"}), 404

    try:
        crud.vote.record(db, user_id=current_user.id, entry_id=id, value=value)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry = crud.entry.get_with_user_vote(db, id=id, user_id=current_user.id)
    if entry.type == 3:
        template_name = "questions/_vote_comment.html"
    else:
        template_name = "questions/_vote_large.html"

    return render_template(template_name, entry=entry)


@bp.route("/entries/<int:id>", methods=["DELETE"])
@login_required
def delete_entry(id: int):
    try:
        crud.entry.mark_as_deleted(db, id=id, user_id=current_user.id)
    except NoResultFound:
        abort(404)

    return "", 204
