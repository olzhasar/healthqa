from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.widgets import PasswordInput


class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        [
            validators.InputRequired(),
            validators.Email(message="Your email is not valid"),
        ],
        description="Your email address",
    )
    name = StringField(
        "Name",
        [
            validators.InputRequired(),
            validators.Length(min=3, message="Name must be at least 3 characters long"),
        ],
        description="Your display name",
    )
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


class LoginForm(FlaskForm):
    email = StringField("Email", [validators.InputRequired()])
    password = StringField(
        "Password",
        [validators.InputRequired()],
        widget=PasswordInput(),
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


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", [validators.InputRequired()])
