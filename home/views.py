from flask import Blueprint, render_template

from crud import question as question_crud
from db.database import db

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    questions = question_crud.get_all(db)
    return render_template("index.html", questions=questions)
