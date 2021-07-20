from flask import Blueprint, render_template

import crud
from db.database import db

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = crud.question.get_all(db)
    tags = crud.tag.get_all(db)
    return render_template("index.html", questions=questions, tags=tags)
