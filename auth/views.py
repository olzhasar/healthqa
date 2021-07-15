from flask import Blueprint, redirect, render_template

from auth.forms import SignupForm
from crud.users import create_user
from db.database import db

bp = Blueprint("auth", __name__, template_folder="templates")


@bp.route("/login")
def login():
    return render_template("login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        create_user(
            db,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        return redirect("/")
    return render_template("signup.html", form=form)
