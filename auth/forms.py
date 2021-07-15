from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, validators

from crud.users import email_exists, username_exists
from db.database import db


class SignupForm(FlaskForm):
    username = StringField(
        "Username", [validators.InputRequired(), validators.Length(min=4)]
    )
    email = StringField("Email", [validators.InputRequired(), validators.Email()])
    password = StringField(
        "Password",
        [
            validators.InputRequired(),
            validators.Length(min=6),
            validators.EqualTo("password_repeat", message="Passwords mismatch"),
        ],
    )
    password_repeat = StringField(
        "Repeat password", [validators.InputRequired(), validators.Length(min=6)]
    )

    def validate_email(form, field):
        if email_exists(db, field.data):
            raise ValidationError(
                "User with this email is already registered. Try login instead"
            )

    def validate_username(form, field):
        if username_exists(db, field.data):
            raise ValidationError(f"Username {field.data} is already taken")
