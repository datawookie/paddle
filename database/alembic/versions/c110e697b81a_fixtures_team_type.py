"""Fixtures: Team Type

Revision ID: c110e697b81a
Revises: a82fa9a9e38b
Create Date: 2023-02-16 06:38:34.017558

"""
from alembic import op
import database as db


# revision identifiers, used by Alembic.
revision = "c110e697b81a"
down_revision = "a82fa9a9e38b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.bulk_insert(
        db.TeamType.__table__,
        [
            {"label": "Junior"},
            {"label": "Senior"},
        ],
    )


def downgrade() -> None:
    pass
