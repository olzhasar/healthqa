"""Tags data

Revision ID: 7a57533e6d28
Revises: 284c341ef788
Create Date: 2021-08-26 16:59:29.187954

"""
import sqlalchemy as sa
from slugify import slugify

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "7a57533e6d28"
down_revision = "284c341ef788"
branch_labels = None
depends_on = None

TAGS = {
    "Conditions": [
        "Ankylosing Spondylitis",
        "Arthritis",
        "Bulging disc",
        "Degenerative disc disease",
        "Fibromyalgia",
        "Herniated disc",
        "Kyphosis",
        "Muscle strain",
        "Osteoporosis",
        "Piriformis Syndrome",
        "Rheumatoid Arthritis",
        "Sciatica",
        "Scoliosis",
        "Spinal Cord Injury",
        "Spinal Fracture",
        "Spinal Stenosis",
        "Spinal Tumor",
        "Spondylolisthesis",
        "Spondylosis (Osteoarthritis)",
        "Upper-Crossed Syndrome",
        "Whiplash",
    ],
    "Pain areas": [
        "Arm pain",
        "Leg pain",
        "Lower back pain",
        "Neck pain",
        "Pelvic floor pain",
        "SI Joint pain",
        "Sitting bone pain",
        "Tailbone pain",
        "Upper back pain",
    ],
}


def upgrade():
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrades()


def downgrade():
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrades()


def data_upgrades():
    tag_categories_table = sa.table(
        "tag_categories",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    tags_table = sa.table(
        "tags",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
        sa.column("category_id", sa.Integer),
    )

    op.bulk_insert(
        tag_categories_table,
        [{"id": i, "name": name} for i, name in enumerate(TAGS.keys(), 1)],
    )

    for i, (category_name, tags) in enumerate(TAGS.items(), 1):
        op.bulk_insert(
            tags_table,
            [{"category_id": i, "name": name, "slug": slugify(name)} for name in tags],
        )


def data_downgrades():
    for i in range(1, len(TAGS) + 1):
        op.execute("DELETE FROM tags WHERE category_id = %s" % i)
        op.execute("DELETE FROM tag_categories WHERE id = %s" % i)
