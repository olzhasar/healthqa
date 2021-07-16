from flask import Blueprint, redirect, render_template
from flask_login import login_user

from app.security import check_password
from auth import forms
from crud.users import create_user, get_by_username_or_email
from db.database import db

bp = Blueprint("auth", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = get_by_username_or_email(db, form.username_or_email.data)
        if user and check_password(form.password.data, user.password):
            login_user(user)
            return redirect("/")
        error = "Invalid credentials"

    return render_template("login.html", form=form, error=error)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = forms.SignupForm()
    if form.validate_on_submit():
        create_user(
            db,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        return redirect("/")
    return render_template("signup.html", form=form)
