from flask import Blueprint, render_template
from flask_login import login_required

from db.database import db

bp = Blueprint(
    "questions", __name__, template_folder="templates", url_prefix="/questions"
)


@bp.route("/<question_id>")
def details(question_id: int):
    return render_template("details.html")


@bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask():
    return render_template("ask_question.html")
