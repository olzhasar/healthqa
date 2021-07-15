from flask import Blueprint, render_template

bp = Blueprint("auth", __name__, template_folder="templates/auth")


@bp.route("/login")
def login():
    return render_template("login.html")


@bp.route("/signup")
def signup():
    return render_template("signup.html")
