from flask import Blueprint, render_template

bp = Blueprint("home", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/search")
def search():
    return "Not implemented"
