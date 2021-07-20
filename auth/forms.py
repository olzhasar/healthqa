from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, validators
from wtforms.widgets import PasswordInput

import crud
from db.database import db


class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        [validators.InputRequired(), validators.Email()],
        description="Your email address",
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
        if crud.user.email_exists(db, field.data):
            raise ValidationError("User with this email is already registered")


class LoginForm(FlaskForm):
    email = StringField("Email", [validators.InputRequired()])
    password = StringField(
        "Password",
        [validators.InputRequired()],
        widget=PasswordInput(),
    )
