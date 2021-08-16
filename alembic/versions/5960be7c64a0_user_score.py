"""User score

Revision ID: 5960be7c64a0
Revises: 6809ac08d2b5
Create Date: 2021-08-16 19:13:14.410265

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5960be7c64a0"
down_revision = "6809ac08d2b5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("score", sa.Integer(), nullable=True))
    op.execute("UPDATE users SET score = 0")
    op.alter_column("users", "score", nullable=False)
    op.create_index(op.f("ix_users_score"), "users", ["score"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_score"), table_name="users")
    op.drop_column("users", "score")
    # ### end Alembic commands ###
