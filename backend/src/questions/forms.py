from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, validators

from common.forms import RichField, TagsField


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
        render_kw={"class": "h-64 overflow-y-scroll"},
    )

    tags = TagsField(
        "Tags",
        description="Tags",
        coerce=int,
        validate_choice=False,
        validators=[
            validators.InputRequired("Please, select at least one tag for your question")
        ],
    )


class AnswerForm(FlaskForm):
    content = RichField(
        "Content",
        [
            validators.InputRequired(),
            validators.Length(min=20),
        ],
        description="Answer content",
        render_kw={"class": "h-64 overflow-y-scroll"},
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


class VoteForm(FlaskForm):
    value = IntegerField("Value", [validators.InputRequired()])
