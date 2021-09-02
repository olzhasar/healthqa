import random

import click

from app.main import app
from storage import store
from tests.factories import (
    AnswerFactory,
    CommentFactory,
    QuestionFactory,
    TagCategoryFactory,
    TagFactory,
    UserFactory,
    VoteFactory,
)


@click.group()
def cli():
    pass


@cli.command("create_test_data")
def test_data():
    with app.app_context():
        factories = [
            AnswerFactory,
            CommentFactory,
            QuestionFactory,
            TagCategoryFactory,
            TagFactory,
            UserFactory,
            VoteFactory,
        ]

        for f in factories:
            f._meta.sqlalchemy_session = store.db
            f._meta.sqlalchemy_session_persistence = "flush"

        categories = TagCategoryFactory.create_batch(5)
        tags = []

        for category in categories:
            tags.extend(TagFactory.create_batch(random.randint(3, 7), category=category))

        for _ in range(10):
            questions = QuestionFactory.create_batch(
                3, tags=random.choices(tags, k=random.randint(2, 4))
            )

            for question in questions:
                for answer in AnswerFactory.create_batch(3, question=question):
                    VoteFactory.create_batch(random.randint(1, 7), entry_id=answer.id)

                    for comment in CommentFactory.create_batch(
                        random.randint(1, 4), entry_id=answer.id
                    ):
                        VoteFactory.create_batch(
                            random.randint(1, 7), entry_id=comment.id, value=1
                        )

                for comment in CommentFactory.create_batch(
                    random.randint(1, 4), entry_id=question.id
                ):
                    VoteFactory.create_batch(
                        random.randint(1, 7), entry_id=comment.id, value=1
                    )

                VoteFactory.create_batch(random.randint(1, 7), entry_id=question.id)

            store.db.commit()


@cli.command()
def run():
    app.run()


if __name__ == "__main__":
    cli()
