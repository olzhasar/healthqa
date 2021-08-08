"""Answer

Revision ID: 80671ff57441
Revises: 7bdf692fb915
Create Date: 2021-08-08 20:52:31.001618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80671ff57441'
down_revision = '7bdf692fb915'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('edited_at', sa.DateTime(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['entries.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answers_question_id'), 'answers', ['question_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_answers_question_id'), table_name='answers')
    op.drop_table('answers')
    # ### end Alembic commands ###
