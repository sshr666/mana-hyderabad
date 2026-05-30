"""create complaints

Revision ID: 20260530_0001
Revises:
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260530_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    supported_language = sa.Enum("en", "te", "hi", "ur", name="supported_language")
    complaint_category = sa.Enum(
        "SANITATION",
        "DRAINAGE",
        "WATERLOGGING",
        "ROADS",
        "STREET_LIGHTS",
        "WATER_SUPPLY",
        "TRAFFIC",
        "PUBLIC_HEALTH",
        "OTHER",
        name="complaint_category",
    )
    complaint_department = sa.Enum(
        "SANITATION",
        "DRAINAGE",
        "ROADS",
        "ELECTRICAL",
        "WATER_SUPPLY",
        "TRAFFIC",
        "PUBLIC_HEALTH",
        "MULTI_DEPARTMENT",
        "MANUAL_REVIEW",
        name="complaint_department",
    )
    complaint_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "EMERGENCY", name="complaint_priority")
    complaint_status = sa.Enum("SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", name="complaint_status")
    analysis_source = sa.Enum("LLM", "FALLBACK_RULES", "MANUAL", name="analysis_source")

    op.create_table(
        "complaints",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True, nullable=False),
        sa.Column("reference_id", sa.String(length=32), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_english_text", sa.Text(), nullable=True),
        sa.Column("original_language", supported_language, nullable=True),
        sa.Column("detected_language", sa.String(length=16), nullable=True),
        sa.Column("category", complaint_category, nullable=False),
        sa.Column("subcategory", sa.String(length=96), nullable=True),
        sa.Column("department", complaint_department, nullable=True),
        sa.Column("priority", complaint_priority, nullable=False),
        sa.Column("status", complaint_status, server_default="SUBMITTED", nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("location", geoalchemy2.Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True),
        sa.Column("landmark", sa.String(length=255), nullable=True),
        sa.Column("locality", sa.String(length=120), nullable=True),
        sa.Column("ward_name", sa.String(length=120), nullable=True),
        sa.Column("ward_number", sa.Integer(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("assigned_team", sa.String(length=120), nullable=True),
        sa.Column("internal_note", sa.Text(), nullable=True),
        sa.Column("analysis_source", analysis_source, nullable=True),
        sa.Column("requires_human_verification", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("reasoning_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_complaints_reference_id", "complaints", ["reference_id"], unique=True)
    op.create_index("ix_complaints_category", "complaints", ["category"])
    op.create_index("ix_complaints_priority", "complaints", ["priority"])
    op.create_index("ix_complaints_status", "complaints", ["status"])
    op.create_index("ix_complaints_locality", "complaints", ["locality"])
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])
    op.create_index("ix_complaints_location", "complaints", ["location"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_complaints_location", table_name="complaints", postgresql_using="gist")
    op.drop_index("ix_complaints_created_at", table_name="complaints")
    op.drop_index("ix_complaints_locality", table_name="complaints")
    op.drop_index("ix_complaints_status", table_name="complaints")
    op.drop_index("ix_complaints_priority", table_name="complaints")
    op.drop_index("ix_complaints_category", table_name="complaints")
    op.drop_index("ix_complaints_reference_id", table_name="complaints")
    op.drop_table("complaints")
    op.execute("DROP TYPE IF EXISTS analysis_source")
    op.execute("DROP TYPE IF EXISTS complaint_status")
    op.execute("DROP TYPE IF EXISTS complaint_priority")
    op.execute("DROP TYPE IF EXISTS complaint_department")
    op.execute("DROP TYPE IF EXISTS complaint_category")
    op.execute("DROP TYPE IF EXISTS supported_language")
