from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.widgets import PasswordInput


class ProfileForm(FlaskForm):
    name = StringField(
        "Name",
        [
            validators.InputRequired(),
            validators.Length(min=3, message="Name must be at least 3 characters long"),
        ],
        description="Your display name",
    )


class SetPasswordForm(FlaskForm):
    password = StringField(
        "Password",
        [
            validators.InputRequired(),
            validators.Length(
                min=6, message="Password must be at least 6 characters long"
            ),
        ],
        widget=PasswordInput(),
        description="************",
    )
    password_repeat = StringField(
        "Repeat password",
        [
            validators.InputRequired(),
            validators.EqualTo(
                "password", message="Please make sure your passwords match"
            ),
        ],
        widget=PasswordInput(),
        description="************",
    )


class ChangePasswordForm(SetPasswordForm):
    current_password = StringField(
        "Current password",
        [validators.InputRequired()],
        widget=PasswordInput(),
        description="************",
    )
