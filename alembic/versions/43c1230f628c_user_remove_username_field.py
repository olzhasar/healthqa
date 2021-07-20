"""User remove username field

Revision ID: 43c1230f628c
Revises: c3c1c2501df5
Create Date: 2021-07-20 14:54:35.610114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43c1230f628c'
down_revision = 'c3c1c2501df5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    # ### end Alembic commands ###
