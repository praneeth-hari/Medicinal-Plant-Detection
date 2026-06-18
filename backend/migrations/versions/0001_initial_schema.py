"""Initial schema — represents tables created by init_db() before Alembic adoption.

Revision ID: 0001
Revises:     None
Create Date: 2026-06-13

This revision is a no-op.  The plants, users, chat, and detection tables
were created directly by SQLAlchemy's create_all() (init_db).
It exists so that ``alembic stamp 0001`` can mark the current database
as being at this revision before migration 0002 is applied.
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables already exist — nothing to do.
    pass


def downgrade() -> None:
    pass
