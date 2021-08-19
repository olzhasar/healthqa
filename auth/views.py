from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required
from sqlalchemy.exc import NoResultFound

import crud
from auth import forms, security
from auth.services import generate_and_send_verification_link
from db.database import db

bp = Blueprint("auth", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    error = None

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = crud.user.get_by_email(db, email=form.email.data)
        if user and security.check_password(form.password.data, user.password):
            if not user.email_verified:
                generate_and_send_verification_link(user)
                return redirect(url_for("auth.verification_required"))

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
        generate_and_send_verification_link(user)
        return redirect(url_for("auth.verification_required"))
    return render_template("signup.html", form=form)


@bp.route("/verification_required")
def verification_required():
    return render_template("verification_required.html")


@bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        abort(401)

    logout_user()
    flash("You have been logged out successfully")

    return redirect(url_for("home.index"))


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = forms.ChangePasswordForm()
    if form.validate_on_submit():
        if security.check_password(form.current_password.data, current_user.password):
            crud.user.change_password(
                db, user_id=current_user.id, new_password=form.password.data
            )
            flash("Your password has been changed successfully")

            return redirect(url_for("users.profile", id=current_user.id))

        form.current_password.errors.append("Invalid old password")

    return render_template("change_password.html", form=form)


@bp.route("/verify_email/<string:token>")
def verify_email(token: str):
    try:
        user_id = security.get_user_id_from_token(
            token, max_age=current_app.config["TOKEN_MAX_AGE_EMAIL_VERIFICATION"]
        )
    except ValueError:
        return render_template("invalid_token.html")

    try:
        user = crud.user.get(db, id=user_id)
    except NoResultFound:
        return render_template("invalid_token.html")

    crud.user.mark_email_verified(db, user=user)
    login_user(user)
    flash("Your account has been activated")
    return redirect(url_for("home.index"))
