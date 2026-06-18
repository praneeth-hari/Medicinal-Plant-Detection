"""Add role column to users table.

Revision ID: 0003
Revises:     0002
Create Date: 2026-06-13

Purely additive — adds a single nullable VARCHAR column with a
server-side default of 'customer'.  Existing rows will receive
'customer' via the DEFAULT clause on next write; a one-time UPDATE
is included in upgrade() to backfill immediately.
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default="customer",
        ),
    )
    # Backfill any rows that were created before this migration
    op.execute("UPDATE users SET role = 'customer' WHERE role IS NULL OR role = ''")


def downgrade() -> None:
    # SQLite < 3.35 does not support DROP COLUMN — no-op
    pass
