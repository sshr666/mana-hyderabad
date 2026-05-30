"""create complaints

Revision ID: 20260530_0001
Revises:
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa

revision: str = "20260530_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    supported_language = sa.Enum("en", "te", "hi", "ur", name="supported_language")
    complaint_category = sa.Enum(
        "SANITATION",
        "DRAINAGE",
        "WATERLOGGING",
        "ROADS",
        "STREET_LIGHTS",
        "WATER_SUPPLY",
        "TRAFFIC",
        "OTHER",
        name="complaint_category",
    )
    complaint_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "EMERGENCY", name="complaint_priority")
    complaint_status = sa.Enum("SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", name="complaint_status")

    supported_language.create(op.get_bind(), checkfirst=True)
    complaint_category.create(op.get_bind(), checkfirst=True)
    complaint_priority.create(op.get_bind(), checkfirst=True)
    complaint_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("reference_id", sa.String(length=32), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_english_text", sa.Text(), nullable=False),
        sa.Column("original_language", supported_language, nullable=False),
        sa.Column("category", complaint_category, nullable=False),
        sa.Column("subcategory", sa.String(length=96), nullable=False),
        sa.Column("priority", complaint_priority, nullable=False),
        sa.Column("status", complaint_status, nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("landmark", sa.String(length=255), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("assigned_team", sa.String(length=120), nullable=True),
        sa.Column("location", geoalchemy2.Geography(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_complaints_id", "complaints", ["id"])
    op.create_index("ix_complaints_reference_id", "complaints", ["reference_id"], unique=True)
    op.create_index("ix_complaints_location", "complaints", ["location"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_complaints_location", table_name="complaints", postgresql_using="gist")
    op.drop_index("ix_complaints_reference_id", table_name="complaints")
    op.drop_index("ix_complaints_id", table_name="complaints")
    op.drop_table("complaints")
    op.execute("DROP TYPE IF EXISTS complaint_status")
    op.execute("DROP TYPE IF EXISTS complaint_priority")
    op.execute("DROP TYPE IF EXISTS complaint_category")
    op.execute("DROP TYPE IF EXISTS supported_language")
