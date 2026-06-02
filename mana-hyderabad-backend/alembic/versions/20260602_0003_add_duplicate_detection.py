"""add duplicate detection

Revision ID: 20260602_0003
Revises: 20260602_0002
Create Date: 2026-06-02
"""
from __future__ import annotations

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

try:
    from pgvector.sqlalchemy import Vector
except ImportError:  # pragma: no cover
    Vector = None  # type: ignore[assignment]


revision: str = "20260602_0003"
down_revision: Union[str, None] = "20260602_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    if Vector is None:
        raise RuntimeError("pgvector must be installed before running this migration")

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    duplicate_resolution_status = sa.Enum(
        "CONFIRMED_DUPLICATE",
        "KEEP_SEPARATE",
        name="duplicate_resolution_status",
    )
    duplicate_confidence = sa.Enum("LOW", "MEDIUM", "HIGH", name="duplicate_confidence")
    duplicate_suggestion_status = sa.Enum(
        "PENDING_REVIEW",
        "CONFIRMED_DUPLICATE",
        "REJECTED",
        "DISMISSED",
        name="duplicate_suggestion_status",
    )
    duplicate_resolution_status.create(op.get_bind(), checkfirst=True)
    duplicate_confidence.create(op.get_bind(), checkfirst=True)
    duplicate_suggestion_status.create(op.get_bind(), checkfirst=True)

    op.add_column("complaints", sa.Column("embedding", Vector(dimensions), nullable=True))
    op.add_column("complaints", sa.Column("embedding_generated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("complaints", sa.Column("embedding_source_text", sa.Text(), nullable=True))
    op.add_column("complaints", sa.Column("duplicate_of_reference_id", sa.String(length=32), nullable=True))
    op.add_column(
        "complaints",
        sa.Column("duplicate_resolution_status", duplicate_resolution_status, nullable=True),
    )
    op.create_index("ix_complaints_duplicate_of_reference_id", "complaints", ["duplicate_of_reference_id"])

    op.create_table(
        "complaint_duplicate_suggestions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("source_complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("distance_meters", sa.Float(), nullable=False),
        sa.Column("time_difference_hours", sa.Float(), nullable=False),
        sa.Column("semantic_similarity", sa.Float(), nullable=True),
        sa.Column("category_match", sa.Boolean(), nullable=False),
        sa.Column("duplicate_score", sa.Float(), nullable=False),
        sa.Column("confidence_label", duplicate_confidence, nullable=False),
        sa.Column(
            "status",
            duplicate_suggestion_status,
            server_default="PENDING_REVIEW",
            nullable=False,
        ),
        sa.Column("reviewed_by", sa.String(length=120), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["candidate_complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_complaint_id", "candidate_complaint_id", name="uq_duplicate_source_candidate"),
    )
    op.create_index(
        "ix_duplicate_suggestions_source_complaint_id",
        "complaint_duplicate_suggestions",
        ["source_complaint_id"],
    )
    op.create_index(
        "ix_duplicate_suggestions_candidate_complaint_id",
        "complaint_duplicate_suggestions",
        ["candidate_complaint_id"],
    )
    op.create_index("ix_duplicate_suggestions_status", "complaint_duplicate_suggestions", ["status"])
    op.create_index(
        "ix_duplicate_suggestions_duplicate_score",
        "complaint_duplicate_suggestions",
        ["duplicate_score"],
    )
    op.create_index("ix_duplicate_suggestions_created_at", "complaint_duplicate_suggestions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_duplicate_suggestions_created_at", table_name="complaint_duplicate_suggestions")
    op.drop_index("ix_duplicate_suggestions_duplicate_score", table_name="complaint_duplicate_suggestions")
    op.drop_index("ix_duplicate_suggestions_status", table_name="complaint_duplicate_suggestions")
    op.drop_index("ix_duplicate_suggestions_candidate_complaint_id", table_name="complaint_duplicate_suggestions")
    op.drop_index("ix_duplicate_suggestions_source_complaint_id", table_name="complaint_duplicate_suggestions")
    op.drop_table("complaint_duplicate_suggestions")
    op.drop_index("ix_complaints_duplicate_of_reference_id", table_name="complaints")
    op.drop_column("complaints", "duplicate_resolution_status")
    op.drop_column("complaints", "duplicate_of_reference_id")
    op.drop_column("complaints", "embedding_source_text")
    op.drop_column("complaints", "embedding_generated_at")
    op.drop_column("complaints", "embedding")
    op.execute("DROP TYPE IF EXISTS duplicate_suggestion_status")
    op.execute("DROP TYPE IF EXISTS duplicate_confidence")
    op.execute("DROP TYPE IF EXISTS duplicate_resolution_status")
