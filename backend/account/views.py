from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

import crud
from account import forms
from auth import security
from db.database import db

bp = Blueprint("account", __name__, url_prefix="/account", template_folder="templates")


@bp.route("/")
def index():
    return redirect(url_for("account.edit_info"), 301)


@bp.route("/info", methods=["GET", "POST"])
@login_required
def edit_info():
    form = forms.ProfileForm(obj=current_user)
    if form.validate_on_submit():
        crud.user.update(db, user_id=current_user.id, name=form.name.data)
        flash("Account information has been updated")

    return render_template("edit_info.html", form=form)


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
