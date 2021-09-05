from flask import Blueprint, render_template

import repository as repo
from storage import store

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = repo.question.all(store, limit=20)
    return render_template("home/index.html", questions=questions)


@bp.route("/about")
def about():
    return render_template("home/about.html")
