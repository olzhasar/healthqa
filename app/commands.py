import random

from flask import Flask

from db.database import db
from tests.factories import (
    AnswerFactory,
    CommentFactory,
    QuestionFactory,
    TagFactory,
    UserFactory,
    VoteFactory,
)


def init_app(app: Flask):
    @app.cli.command("generate_test_data")
    def generate_test_data():
        if app.config["TESTING"] is True:
            return

        factories = [
            AnswerFactory,
            CommentFactory,
            QuestionFactory,
            TagFactory,
            UserFactory,
            VoteFactory,
        ]

        for f in factories:
            f._meta.sqlalchemy_session = db

        for _ in range(10):
            tags = TagFactory.create_batch(3)

            questions = QuestionFactory.create_batch(3, tags=tags)

            for question in questions:
                for answer in AnswerFactory.create_batch(3, question=question):
                    VoteFactory.create_batch(random.randint(1, 7), entry_id=answer.id)

                    for comment in CommentFactory.create_batch(
                        random.randint(1, 4), entry_id=answer.id
                    ):
                        VoteFactory.create_batch(3, entry_id=comment.id, value=1)

                for comment in CommentFactory.create_batch(
                    random.randint(1, 4), entry_id=question.id
                ):
                    VoteFactory.create_batch(
                        random.randint(1, 7), entry_id=comment.id, value=1
                    )

                VoteFactory.create_batch(random.randint(1, 7), entry_id=question.id)

            db.commit()
