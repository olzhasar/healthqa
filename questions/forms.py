from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    validators,
)

from common.forms import RichField


class AskQuestionForm(FlaskForm):
    title = StringField(
        "Title",
        [
            validators.InputRequired(),
            validators.Length(min=15, max=150),
        ],
        description="Question title",
    )

    content = RichField(
        "Content",
        [
            validators.InputRequired(),
            validators.Length(min=20),
        ],
        description="Question content",
        render_kw={"rows": 16},
    )

    tags = SelectMultipleField("Tags", description="Tags")


class AnswerForm(FlaskForm):
    content = RichField(
        "Content",
        [
            validators.InputRequired(),
            validators.Length(min=20),
        ],
        description="Answer content",
        render_kw={"rows": 16},
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        "Content",
        [
            validators.InputRequired(message="Content field is required"),
            validators.Length(
                min=15, message="Make sure your comment is at least 15 symbols long"
            ),
        ],
        description="Question content",
        render_kw={"rows": 4},
    )
