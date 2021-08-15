from flask_wtf import FlaskForm
from wtforms import StringField, validators


class ProfileForm(FlaskForm):
    name = StringField(
        "Name",
        [
            validators.InputRequired(),
            validators.Length(min=3, message="Name must be at least 3 characters long"),
        ],
        description="Your display name",
    )
