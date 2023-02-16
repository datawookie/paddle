"""Fixtures: Category

Revision ID: 09b05f0d065c
Revises: 915a89d96e8b
Create Date: 2023-02-16 06:04:50.127554

"""
from alembic import op
import database as db


# revision identifiers, used by Alembic.
revision = "09b05f0d065c"
down_revision = "915a89d96e8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for category in db.CATEGORY_LIST:
        op.bulk_insert(
            db.Category.__table__,
            [{"label": category}],
        )


def downgrade() -> None:
    pass
