"""Fixtures: Number

Revision ID: a82fa9a9e38b
Revises: 09b05f0d065c
Create Date: 2023-02-16 06:07:28.491831

"""
from alembic import op

import database as db

# revision identifiers, used by Alembic.
revision = "a82fa9a9e38b"
down_revision = "09b05f0d065c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for number in range(db.MAX_NUMBER):
        op.bulk_insert(
            db.Number.__table__,
            [{"id": number + 1}],
        )


def downgrade() -> None:
    pass
