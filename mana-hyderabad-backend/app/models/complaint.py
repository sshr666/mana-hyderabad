import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
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
    OTHER = "OTHER"


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


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_english_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_language: Mapped[SupportedLanguage] = mapped_column(
        Enum(SupportedLanguage, name="supported_language"),
        nullable=False,
        default=SupportedLanguage.en,
    )
    category: Mapped[ComplaintCategory] = mapped_column(
        Enum(ComplaintCategory, name="complaint_category"),
        nullable=False,
    )
    subcategory: Mapped[str] = mapped_column(String(96), nullable=False)
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
    landmark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    assigned_team: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
