from faker import Faker

import crud
from models import Answer

fake = Faker()


def test_create_answer(db, user, question):
    content = fake.paragraph()

    answer = crud.answer.create(
        db,
        user=user,
        question_id=question.id,
        content=content,
    )

    assert isinstance(answer, Answer)
    assert answer.id
    assert answer.user == user
    assert answer.question == question
    assert answer.content == content

    assert db.query(Answer).filter(Answer.user_id == user.id).first() == answer
