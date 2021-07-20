"""User name

Revision ID: 97049da19ed1
Revises: 43c1230f628c
Create Date: 2021-07-20 18:46:42.716398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97049da19ed1'
down_revision = '43c1230f628c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'name')
    # ### end Alembic commands ###