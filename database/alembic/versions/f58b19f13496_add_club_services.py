"""Add club.services

Revision ID: f58b19f13496
Revises: 4f370a25634c
Create Date: 2023-03-07 05:48:30.625844

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f58b19f13496"
down_revision = "4f370a25634c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "club",
        sa.Column("services", sa.Boolean(), server_default=sa.text("0"), nullable=True),
    )


def downgrade() -> None:
    op.add_column("entry", sa.Column("series", sa.BOOLEAN(), nullable=True))
