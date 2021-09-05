from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from flask.globals import current_app
from flask_login import current_user, login_required

import repository as repo
from questions import forms
from storage import store

bp = Blueprint("questions", __name__)


@bp.route("/questions/ask", methods=["GET", "POST"])
@login_required
def ask():
    form = forms.AskQuestionForm()
    form.tags.choices = repo.tag_category.all(store)

    if form.validate_on_submit():
        question = repo.question.create(
            store,
            user=current_user,
            title=form.title.data,
            content=form.content.data,
            tags=form.tags.data,
        )
        return redirect(question.url)

    return render_template("questions/ask_question.html", form=form)


@bp.route("/questions/")
def all():
    page = int(request.args.get("page", 1))
    per_page = current_app.config["PAGINATION"]

    paginator = repo.question.list(store, page=page, per_page=per_page)

    return render_template(
        "questions/list.html",
        paginator=paginator,
    )


@bp.route("/tags/")
def tags():
    return render_template("questions/tag_list.html")


@bp.route("/tags/<string:slug>/")
def by_tag(slug: str):
    tag = repo.tag.get_by_slug(store, slug)

    page = int(request.args.get("page", 1))
    per_page = current_app.config["PAGINATION"]

    paginator = repo.question.list_by_tag(store, tag, page=page, per_page=per_page)

    return render_template(
        "questions/list.html",
        page_title=f'Results for "{tag.name}"',
        paginator=paginator,
    )


@bp.route("/questions/search")
def search():
    query = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    per_page = current_app.config["PAGINATION"]

    paginator = repo.question.search(store, query, page=page, per_page=per_page)

    return render_template(
        "questions/search_results.html",
        query=query,
        paginator=paginator,
    )


@bp.route("/questions/<int:id>", strict_slashes=False)
@bp.route("/questions/<int:id>/<string:slug>")
def details(id: int, slug: str = None):
    additional_params = {}
    if current_user.is_authenticated:
        additional_params["user_id"] = current_user.id

    question = repo.question.get_with_related(store, id, **additional_params)
    if slug != question.slug:
        return redirect(url_for("questions.details", id=id, slug=question.slug), 301)

    remote_addr = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    if remote_addr:
        repo.question.register_view(store, id, remote_addr)

    answers = repo.answer.all_for_question(
        store, question_id=question.id, **additional_params
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
    question = repo.question.get(store, id)
    if question.user != current_user:
        abort(403)

    form = forms.AskQuestionForm(obj=question)
    form.tags.choices = repo.tag_category.all(store)

    if form.validate_on_submit():
        repo.question.update(
            store,
            question,
            new_title=form.title.data,
            new_content=form.content.data,
            tags=form.tags.data,
        )
        return redirect(question.url)

    return render_template("questions/question_edit.html", form=form)


@bp.route("/questions/<int:id>/answer", methods=["POST"])
@login_required
def answer(id: int):
    if not repo.question.exists(store, id):
        return jsonify({"error": "invalid question_id"}), 403

    form = forms.AnswerForm()
    if form.validate_on_submit():
        answer = repo.answer.create(
            store,
            user=current_user,
            question_id=id,
            content=form.content.data,
        )

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
    answer = repo.answer.get(store, id)
    if answer.user != current_user:
        abort(403)

    form = forms.AnswerForm(obj=answer)
    if form.validate_on_submit():
        repo.answer.update(store, answer, new_content=form.content.data)
        return redirect(answer.url)

    return render_template("questions/answer_edit.html", form=form)


@bp.route("/entries/<int:id>/comment", methods=["POST"])
@login_required
def comment(id: int):
    if not repo.entry.exists(store, id):
        return jsonify({"error": "invalid entry_id"}), 400

    form = forms.CommentForm()
    if form.validate_on_submit():
        comment = repo.comment.create(
            store,
            user=current_user,
            entry_id=id,
            content=form.content.data,
        )
        return render_template("questions/_comment.html", comment=comment)

    return render_template(
        "questions/_comment_form.html",
        comment_form=form,
        url=request.url,
    )


@bp.route("/comments/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(id: int):
    comment = repo.comment.get_for_user(store, id=id, user_id=current_user.id)

    form = forms.CommentForm(obj=comment)
    if form.validate_on_submit():
        repo.comment.update(store, comment, content=form.content.data)
        return render_template("questions/_comment.html", comment=comment)

    return render_template("questions/_comment_edit.html", form=form, comment=comment)


@bp.route("/entries/<int:id>/vote/<int:value>", methods=["POST"])
@login_required
def vote(id: int, value: int):
    """
    value 1 - upvote
    value 2 - downvote
    """

    if not repo.entry.exists(store, id):
        return jsonify({"error": "invalid entry_id"}), 404

    try:
        repo.vote.record(store, user_id=current_user.id, entry_id=id, value=value)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    entry = repo.entry.get_with_user_vote(store, id=id, user_id=current_user.id)
    if entry.type == 3:
        template_name = "questions/_vote_comment.html"
    else:
        template_name = "questions/_vote_large.html"

    return render_template(template_name, entry=entry)


@bp.route("/entries/<int:id>", methods=["DELETE"])
@login_required
def delete_entry(id: int):
    repo.entry.mark_as_deleted(store, id=id, user_id=current_user.id)
    return "", 204
