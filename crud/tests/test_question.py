from faker import Faker

import crud
from models import Question

fake = Faker()


def test_create_question(db, user, tag, other_tag):
    title = fake.sentence()
    content = fake.paragraph()

    question = crud.question.create(
        db,
        user=user,
        title=title,
        content=content,
        tags=[tag, other_tag],
    )

    assert isinstance(question, Question)
    assert question.id
    assert question.user == user
    assert question.title == title
    assert question.content == content
    assert question.tags == [tag, other_tag]

    assert db.query(Question).filter(Question.user_id == user.id).first() == question
