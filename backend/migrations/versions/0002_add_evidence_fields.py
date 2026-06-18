"""Add evidence-based fields to the plants table.

Revision ID: 0002
Revises:     0001
Create Date: 2026-06-13

PURELY ADDITIVE — no existing columns are modified or dropped.
All new columns are nullable; existing rows will have NULL for all new fields
until they are populated by the pilot seed script.

Column groups added
-------------------
Evidence indexed  : evidence_strength, safety_class, review_status
Evidence text     : native_region, last_reviewed, traditional_uses,
                    evidence_summary, reviewer_notes, overdose_risk
Evidence JSON     : local_names, traditional_systems, regulatory_status,
                    therapeutic_claims, drug_interactions, safety_warnings,
                    active_compounds, dosage_info,
                    preparation_methods_structured,
                    citation_flags, flagged_issues
Evidence booleans : who_monograph_available, ayush_monograph_available
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# ── New columns ───────────────────────────────────────────────────────────────

_INDEXED_COLS = [
    sa.Column("evidence_strength", sa.String(50),  nullable=True),
    sa.Column("safety_class",      sa.String(50),  nullable=True),
    sa.Column("review_status",     sa.String(20),  nullable=True),
]

_TEXT_COLS = [
    sa.Column("native_region",     sa.String(300), nullable=True),
    sa.Column("last_reviewed",     sa.String(10),  nullable=True),
    sa.Column("traditional_uses",  sa.Text,        nullable=True),
    sa.Column("evidence_summary",  sa.Text,        nullable=True),
    sa.Column("reviewer_notes",    sa.Text,        nullable=True),
    sa.Column("overdose_risk",     sa.Text,        nullable=True),
]

_JSON_COLS = [
    sa.Column("local_names",                    sa.Text, nullable=True),
    sa.Column("traditional_systems",            sa.Text, nullable=True),
    sa.Column("regulatory_status",              sa.Text, nullable=True),
    sa.Column("therapeutic_claims",             sa.Text, nullable=True),
    sa.Column("drug_interactions",              sa.Text, nullable=True),
    sa.Column("safety_warnings",               sa.Text, nullable=True),
    sa.Column("active_compounds",              sa.Text, nullable=True),
    sa.Column("dosage_info",                   sa.Text, nullable=True),
    sa.Column("preparation_methods_structured", sa.Text, nullable=True),
    sa.Column("citation_flags",                sa.Text, nullable=True),
    sa.Column("flagged_issues",                sa.Text, nullable=True),
]

_BOOL_COLS = [
    sa.Column("who_monograph_available",   sa.Integer, nullable=False, server_default="0"),
    sa.Column("ayush_monograph_available", sa.Integer, nullable=False, server_default="0"),
]


def upgrade() -> None:
    for col in _INDEXED_COLS + _TEXT_COLS + _JSON_COLS + _BOOL_COLS:
        op.add_column("plants", col)

    # Create indexes for the three filterable columns
    op.create_index("ix_plants_evidence_strength", "plants", ["evidence_strength"])
    op.create_index("ix_plants_safety_class",      "plants", ["safety_class"])
    op.create_index("ix_plants_review_status",     "plants", ["review_status"])


def downgrade() -> None:
    # SQLite does not support DROP COLUMN before version 3.35.
    # Downgrade is a no-op — remove columns manually if required.
    #
    # For PostgreSQL (production):
    #   op.drop_index("ix_plants_review_status",     table_name="plants")
    #   op.drop_index("ix_plants_safety_class",      table_name="plants")
    #   op.drop_index("ix_plants_evidence_strength", table_name="plants")
    #   for col in reversed(_INDEXED_COLS + _TEXT_COLS + _JSON_COLS + _BOOL_COLS):
    #       op.drop_column("plants", col.name)
    pass
