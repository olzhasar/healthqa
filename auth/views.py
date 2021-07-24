from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

import crud
from app.security import check_password
from auth import forms
from db.database import db

bp = Blueprint("auth", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    error = None

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = crud.user.get_by_email(db, form.email.data)
        if user and check_password(form.password.data, user.password):
            login_user(user)
            redirect_url = request.args.get("next", url_for("home.index"))
            return redirect(redirect_url)
        error = "Invalid credentials"

    return render_template("login.html", form=form, error=error)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = forms.SignupForm()
    if form.validate_on_submit():
        user = crud.user.create_user(
            db,
            email=form.email.data,
            name=form.name.data,
            password=form.password.data,
        )
        login_user(user)
        return redirect(url_for("home.index"))
    return render_template("signup.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        abort(401)

    logout_user()
    return redirect(url_for("home.index"))
