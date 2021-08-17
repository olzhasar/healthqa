"""Tag slug

Revision ID: 7fdbf4ff489e
Revises: 871a6baec501
Create Date: 2021-08-17 17:32:50.535421

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "7fdbf4ff489e"
down_revision = "871a6baec501"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tags", sa.Column("slug", sa.String(), nullable=True))
    op.execute("UPDATE tags SET slug = name")
    op.alter_column("tags", "slug", nullable=False)
    op.create_unique_constraint(None, "tags", ["slug"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "tags", type_="unique")
    op.drop_column("tags", "slug")
    # ### end Alembic commands ###
