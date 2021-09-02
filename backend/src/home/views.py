from flask import Blueprint, render_template

import crud
from storage import store

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = crud.question.get_popular_list(store.db, limit=20)
    return render_template("home/index.html", questions=questions)


@bp.route("/about")
def about():
    return render_template("home/about.html")
