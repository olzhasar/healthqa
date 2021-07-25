"""Tag

Revision ID: 7921c27fad66
Revises: 00476c774238
Create Date: 2021-07-25 21:16:53.435147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7921c27fad66'
down_revision = '00476c774238'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags')
    # ### end Alembic commands ###
