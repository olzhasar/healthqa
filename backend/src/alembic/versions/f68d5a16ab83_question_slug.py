"""Question slug

Revision ID: f68d5a16ab83
Revises: 57367419fd8a
Create Date: 2021-09-05 19:10:41.472461

"""
import sqlalchemy as sa
from slugify import slugify

from alembic import op

# revision identifiers, used by Alembic.
revision = "f68d5a16ab83"
down_revision = "57367419fd8a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("questions", sa.Column("slug", sa.String(length=200), nullable=True))
    fill_slugs()
    op.alter_column("questions", "slug", nullable=False)
    # ### end Alembic commands ###


def fill_slugs():
    conn = op.get_bind()

    questions = sa.table(
        "questions",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("slug", sa.String),
    )

    result = conn.execute(sa.select(questions.c.id, questions.c.title))

    data = []
    for question_id, title in result:
        data.append(
            {"question_id": question_id, "question_slug": slugify(title, max_length=64)}
        )

    if data:
        stmt = (
            sa.update(questions)
            .where(questions.c.id == sa.bindparam("question_id"))
            .values(slug=sa.bindparam("question_slug"))
        )
        conn.execute(stmt, data)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("questions", "slug")
    # ### end Alembic commands ###
