"""Fixtures: Club

Revision ID: 915a89d96e8b
Revises: c84b26c56825
Create Date: 2023-02-16 05:46:41.233391

"""

import csv

from alembic import op
from sqlalchemy import text

import database as db

# revision identifiers, used by Alembic.
revision = "915a89d96e8b"
down_revision = "f58b19f13496"
branch_labels = None
depends_on = None


def upgrade() -> None:
    clubs = {}
    with open("club-list.csv", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        # Skip header record.
        next(reader)
        # Group club data by name (for capturing multiple REGEX).
        for row in reader:
            try:
                clubs[row[1]]["regex"].append(row[0])
            except KeyError:
                clubs[row[1]] = {"regex": [row[0]], "services": row[2]}

    for name, data in clubs.items():
        club_regex = "|".join(data["regex"])
        services = bool(int(data["services"]))
        op.bulk_insert(
            db.Club.__table__,
            [{"name": name, "code_regex": club_regex, "services": services}],
        )


def downgrade() -> None:
    pass
