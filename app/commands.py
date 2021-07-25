from flask import Flask

from db.database import db
from tests.factories import (
    AnswerCommentFactory,
    AnswerFactory,
    QuestionCommentFactory,
    QuestionFactory,
    TagFactory,
    UserFactory,
)


def init_app(app: Flask):
    @app.cli.command("generate_test_data")
    def generate_test_data():
        if app.config["TESTING"] is True:
            return

        factories = [
            AnswerFactory,
            AnswerCommentFactory,
            QuestionFactory,
            QuestionCommentFactory,
            TagFactory,
            UserFactory,
        ]

        for f in factories:
            f._meta.sqlalchemy_session = db
            f._meta.sqlalchemy_session_persistence = "flush"

        for _ in range(10):
            tags = TagFactory.create_batch(3)

            questions = QuestionFactory.create_batch(3, tags=tags)

            for question in questions:
                QuestionCommentFactory.create_batch(2, question=question)

                answers = AnswerFactory.create_batch(3, question=question)
                for answer in answers:
                    AnswerCommentFactory.create_batch(2, answer=answer)

            db.commit()
