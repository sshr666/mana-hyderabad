import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ComplaintCategory(str, enum.Enum):
    SANITATION = "SANITATION"
    DRAINAGE = "DRAINAGE"
    WATERLOGGING = "WATERLOGGING"
    ROADS = "ROADS"
    STREET_LIGHTS = "STREET_LIGHTS"
    WATER_SUPPLY = "WATER_SUPPLY"
    TRAFFIC = "TRAFFIC"
    PUBLIC_HEALTH = "PUBLIC_HEALTH"
    OTHER = "OTHER"


class ComplaintDepartment(str, enum.Enum):
    SANITATION = "SANITATION"
    DRAINAGE = "DRAINAGE"
    ROADS = "ROADS"
    ELECTRICAL = "ELECTRICAL"
    WATER_SUPPLY = "WATER_SUPPLY"
    TRAFFIC = "TRAFFIC"
    PUBLIC_HEALTH = "PUBLIC_HEALTH"
    MULTI_DEPARTMENT = "MULTI_DEPARTMENT"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class ComplaintPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"


class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class SupportedLanguage(str, enum.Enum):
    en = "en"
    te = "te"
    hi = "hi"
    ur = "ur"


class AnalysisSource(str, enum.Enum):
    LLM = "LLM"
    FALLBACK_RULES = "FALLBACK_RULES"
    LLM_WITH_GUARDRAILS = "LLM_WITH_GUARDRAILS"
    MANUAL = "MANUAL"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    reference_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_english_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_language: Mapped[SupportedLanguage | None] = mapped_column(
        Enum(SupportedLanguage, name="supported_language"),
        nullable=True,
    )
    detected_language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    category: Mapped[ComplaintCategory] = mapped_column(
        Enum(ComplaintCategory, name="complaint_category"),
        nullable=False,
    )
    subcategory: Mapped[str | None] = mapped_column(String(96), nullable=True)
    department: Mapped[ComplaintDepartment | None] = mapped_column(
        Enum(ComplaintDepartment, name="complaint_department"),
        nullable=True,
    )
    priority: Mapped[ComplaintPriority] = mapped_column(
        Enum(ComplaintPriority, name="complaint_priority"),
        nullable=False,
        default=ComplaintPriority.MEDIUM,
    )
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus, name="complaint_status"),
        nullable=False,
        default=ComplaintStatus.SUBMITTED,
    )

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True)
    landmark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locality: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    ward_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ward_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_team: Mapped[str | None] = mapped_column(String(120), nullable=True)
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis_source: Mapped[AnalysisSource | None] = mapped_column(
        Enum(AnalysisSource, name="analysis_source"),
        nullable=True,
    )
    requires_human_verification: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    reasoning_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
