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

from auth import forms, security
from auth.services import (
    generate_and_send_password_reset_link,
    generate_and_send_verification_link,
)
from repository.exceptions import AlreadyExistsError, NotFoundError
from repository.user import UserRepository

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    error = None

    repo = UserRepository()

    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = repo.get_by_email(form.email.data)
        except NotFoundError:
            pass
        else:
            if security.check_password(form.password.data, user.password):
                if not user.email_verified:
                    generate_and_send_verification_link(user)
                    return redirect(url_for("auth.verification_required"))

                login_user(user)
                redirect_url = request.args.get("next", url_for("home.index"))
                return redirect(redirect_url)
        error = "Invalid credentials"

    return render_template("auth/login.html", form=form, error=error)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = forms.SignupForm()
    if form.validate_on_submit():
        repo = UserRepository()

        try:
            user = repo.create(
                email=form.email.data,
                name=form.name.data,
                password=form.password.data,
            )
        except AlreadyExistsError:
            form.email.errors.append("User with this email is already registered")
        else:
            generate_and_send_verification_link(user)
            return redirect(url_for("auth.verification_required"))
    return render_template("auth/signup.html", form=form)


@bp.route("/verification_required")
def verification_required():
    return render_template("auth/verification_required.html")


@bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        abort(401)

    logout_user()
    flash("You have been logged out successfully")

    return redirect(url_for("home.index"))


@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        repo = UserRepository()

        try:
            user = repo.get_by_email(form.email.data)
        except NotFoundError:
            pass
        else:
            generate_and_send_password_reset_link(user)

        flash(f"Password reset link has been sent to your email: {form.email.data}")
        return redirect(url_for("auth.forgot_password_sent"))

    return render_template("auth/forgot_password.html", form=form)


@bp.route("/forgot_password/sent")
def forgot_password_sent():
    return render_template("auth/forgot_password_sent.html")


@bp.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_password(token: str):
    try:
        user_id = security.get_user_id_from_token(
            token, max_age=current_app.config["TOKEN_MAX_AGE_PASSWORD_RESET"]
        )
    except ValueError:
        return render_template("auth/invalid_token.html")

    repo = UserRepository()
    try:
        user = repo.get(user_id)
    except NotFoundError:
        return render_template("auth/invalid_token.html")

    repo.reset_password(user)
    login_user(user)
    return redirect(url_for("auth.set_password"))


@bp.route("/set_password", methods=["GET", "POST"])
def set_password():
    if not current_user.is_authenticated or current_user.password:
        abort(403)

    form = forms.SetPasswordForm()
    if form.validate_on_submit():
        repo = UserRepository()
        repo.change_password(current_user, new_password=form.password.data)
        flash("Your password has been changed successfully")
        return redirect(url_for("users.profile", id=current_user.id))

    return render_template("auth/set_password.html", form=form)


@bp.route("/verify_email/<string:token>")
def verify_email(token: str):
    try:
        user_id = security.get_user_id_from_token(
            token, max_age=current_app.config["TOKEN_MAX_AGE_EMAIL_VERIFICATION"]
        )
    except ValueError:
        return render_template("auth/invalid_token.html")

    repo = UserRepository()
    try:
        user = repo.get(user_id)
    except NotFoundError:
        return render_template("auth/invalid_token.html")

    repo.mark_email_verified(user)
    login_user(user)
    flash("Welcome on board! Your account has been activated")
    return redirect(url_for("home.index"))
