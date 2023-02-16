"""Fixtures: Club

Revision ID: 915a89d96e8b
Revises: c84b26c56825
Create Date: 2023-02-16 05:46:41.233391

"""
import csv
from alembic import op
import database as db


# revision identifiers, used by Alembic.
revision = "915a89d96e8b"
down_revision = "c84b26c56825"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with open("club-list.csv", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        # Skip header record.
        next(reader)
        for row in reader:
            op.bulk_insert(
                db.Club.__table__,
                [{"id": row[0], "name": row[1]}],
            )


def downgrade() -> None:
    pass
