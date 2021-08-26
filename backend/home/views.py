from flask import Blueprint, render_template

import crud
from db.database import db

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = crud.question.get_popular_list(db, limit=20)
    return render_template("index.html", questions=questions)


@bp.route("/about")
def about():
    return render_template("about.html")
