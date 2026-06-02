"""Add guarded LLM analysis source.

Revision ID: 20260602_0002
Revises: 20260530_0001
Create Date: 2026-06-02
"""

from alembic import op


revision = "20260602_0002"
down_revision = "20260530_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE analysis_source ADD VALUE IF NOT EXISTS 'LLM_WITH_GUARDRAILS'")


def downgrade() -> None:
    # PostgreSQL enum values cannot be removed safely without rebuilding dependent columns.
    pass
