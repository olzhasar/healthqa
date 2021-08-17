from flask import Blueprint, render_template

import crud
from db.database import db

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = crud.question.get_popular_list(db, limit=20)
    tag_categories = crud.tag.get_categories_list(db)
    return render_template(
        "index.html", questions=questions, tag_categories=tag_categories
    )
