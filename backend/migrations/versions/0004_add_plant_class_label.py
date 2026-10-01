"""Add class_label to the plants table.

Revision ID: 0004
Revises:     0003
Create Date: 2026-10-01

Purely additive. ``class_label`` links a plants row to the image classifier's
class folder (see backend/data/models/class_mapping.json). It is nullable and
unique; it stays NULL for every plant whose dataset identity is not confirmed.
SQLite cannot add a UNIQUE column in place, so the uniqueness is enforced with
a separate unique index (the same name the model's ``unique=True, index=True``
produces).
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("plants", sa.Column("class_label", sa.String(100), nullable=True))
    op.create_index("ix_plants_class_label", "plants", ["class_label"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_plants_class_label", table_name="plants")
    # SQLite < 3.35 does not support DROP COLUMN — column is left in place.
