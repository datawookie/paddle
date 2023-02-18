"""Fixtures: Age group

Revision ID: 4f370a25634c
Revises: 702f57ceefe1
Create Date: 2023-02-18 06:15:56.010594

"""
from alembic import op
import database as db


# revision identifiers, used by Alembic.
revision = "4f370a25634c"
down_revision = "c110e697b81a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.bulk_insert(
        db.AgeGroup.__table__,
        [
            {"id": 1, "label": "Junior"},
            {"id": 2, "label": "Senior"},
            {"id": 3, "label": "Veteran"},
            {"id": 4, "label": "Master"},
        ],
    )


def downgrade() -> None:
    pass
