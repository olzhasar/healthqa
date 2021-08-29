import random

from db.database import db
from tests.factories import (
    AnswerFactory,
    CommentFactory,
    QuestionFactory,
    TagCategoryFactory,
    TagFactory,
    UserFactory,
    VoteFactory,
)


def generate_test_data():
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
        f._meta.sqlalchemy_session = db

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

        db.commit()


if __name__ == "__main__":
    generate_test_data()
