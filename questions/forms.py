from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, TextAreaField, validators


class AskQuestionForm(FlaskForm):
    title = StringField(
        "Title",
        [
            validators.InputRequired(),
            validators.Length(max=200),
        ],
        description="Question title",
    )

    content = TextAreaField(
        "Content",
        [
            validators.InputRequired(),
            validators.Length(min=30),
        ],
        description="Question content",
        render_kw={"rows": 16},
    )

    tags = SelectMultipleField("Tags", description="Tags")
