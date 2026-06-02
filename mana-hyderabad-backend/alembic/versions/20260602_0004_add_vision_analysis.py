"""add vision analysis fields

Revision ID: 20260602_0004
Revises: 20260602_0003
Create Date: 2026-06-02
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260602_0004"
down_revision: Union[str, None] = "20260602_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    vision_status = sa.Enum(
        "NOT_REQUESTED",
        "PENDING",
        "COMPLETED",
        "FAILED",
        "NOT_CONFIGURED",
        name="vision_status",
    )
    vision_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "complaints",
        sa.Column("vision_status", vision_status, server_default="NOT_REQUESTED", nullable=True),
    )
    op.add_column("complaints", sa.Column("vision_detected_objects", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("complaints", sa.Column("vision_citizen_message", sa.Text(), nullable=True))
    op.add_column("complaints", sa.Column("vision_admin_summary", sa.Text(), nullable=True))
    op.add_column("complaints", sa.Column("vision_model_version", sa.String(length=120), nullable=True))
    op.add_column("complaints", sa.Column("vision_processed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("complaints", sa.Column("vision_error_code", sa.String(length=64), nullable=True))
    op.add_column(
        "complaints",
        sa.Column("requires_vision_human_verification", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column("complaints", sa.Column("vision_inference_duration_ms", sa.Integer(), nullable=True))
    op.create_index("ix_complaints_vision_status", "complaints", ["vision_status"])
    op.create_index("ix_complaints_vision_processed_at", "complaints", ["vision_processed_at"])


def downgrade() -> None:
    op.drop_index("ix_complaints_vision_processed_at", table_name="complaints")
    op.drop_index("ix_complaints_vision_status", table_name="complaints")
    op.drop_column("complaints", "vision_inference_duration_ms")
    op.drop_column("complaints", "requires_vision_human_verification")
    op.drop_column("complaints", "vision_error_code")
    op.drop_column("complaints", "vision_processed_at")
    op.drop_column("complaints", "vision_model_version")
    op.drop_column("complaints", "vision_admin_summary")
    op.drop_column("complaints", "vision_citizen_message")
    op.drop_column("complaints", "vision_detected_objects")
    op.drop_column("complaints", "vision_status")
    op.execute("DROP TYPE IF EXISTS vision_status")
