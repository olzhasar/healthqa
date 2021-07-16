from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, validators
from wtforms.widgets import PasswordInput

from crud.users import email_exists, username_exists
from db.database import db


class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        [validators.InputRequired(), validators.Email()],
        description="Your email address",
    )
    username = StringField(
        "Username",
        [validators.InputRequired(), validators.Length(min=4)],
        description="Your unique username",
    )
    password = StringField(
        "Password",
        [
            validators.InputRequired(),
            validators.Length(min=6),
            validators.EqualTo(
                "password_repeat", message="Please make sure your passwords match"
            ),
        ],
        widget=PasswordInput(),
        description="************",
    )
    password_repeat = StringField(
        "Repeat password",
        [validators.InputRequired(), validators.Length(min=6)],
        widget=PasswordInput(),
        description="************",
    )

    def validate_email(form, field):
        if email_exists(db, field.data):
            raise ValidationError("User with this email is already registered")

    def validate_username(form, field):
        if username_exists(db, field.data):
            raise ValidationError(f"Username {field.data} is already taken")


class LoginForm(FlaskForm):
    username_or_email = StringField("Username or email", [validators.InputRequired()])
    password = StringField(
        "Password",
        [validators.InputRequired()],
        widget=PasswordInput(),
    )
