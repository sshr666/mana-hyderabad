from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.complaint import ComplaintCategory, ComplaintPriority, ComplaintStatus, SupportedLanguage


Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class ComplaintAnalysisRequest(BaseModel):
    text: Annotated[str, Field(min_length=1)]
    language: SupportedLanguage = SupportedLanguage.en
    photo_url: str | None = Field(default=None, alias="photoUrl")
    latitude: Latitude | None = None
    longitude: Longitude | None = None

    model_config = ConfigDict(populate_by_name=True)


class ComplaintAnalysisResponse(BaseModel):
    normalized_english_text: str = Field(alias="normalizedEnglishText")
    category: ComplaintCategory
    subcategory: str
    priority: ComplaintPriority
    location_text: str | None = Field(alias="locationText")
    missing_fields: list[str] = Field(alias="missingFields")
    follow_up_question: str | None = Field(alias="followUpQuestion")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class ComplaintCreate(BaseModel):
    original_text: Annotated[str, Field(min_length=1)] = Field(alias="originalText")
    normalized_english_text: Annotated[str, Field(min_length=1)] = Field(alias="normalizedEnglishText")
    original_language: SupportedLanguage = Field(default=SupportedLanguage.en, alias="originalLanguage")
    category: ComplaintCategory
    subcategory: Annotated[str, Field(min_length=1)]
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    landmark: str | None = None
    photo_url: str | None = Field(default=None, alias="photoUrl")

    model_config = ConfigDict(populate_by_name=True)


class ComplaintCreateResponse(BaseModel):
    reference_id: str = Field(alias="referenceId")
    status: Literal["SUBMITTED"]
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class ComplaintRead(BaseModel):
    id: int
    reference_id: str = Field(alias="referenceId")
    original_text: str = Field(alias="originalText")
    normalized_english_text: str = Field(alias="normalizedEnglishText")
    original_language: SupportedLanguage = Field(alias="originalLanguage")
    category: ComplaintCategory
    subcategory: str
    priority: ComplaintPriority
    status: ComplaintStatus
    latitude: float | None
    longitude: float | None
    landmark: str | None
    photo_url: str | None = Field(alias="photoUrl")
    department: str
    assigned_team: str | None = Field(alias="assignedTeam")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus | None = None
    department: str | None = None
    assigned_team: str | None = Field(default=None, alias="assignedTeam")
    landmark: str | None = None
    priority: ComplaintPriority | None = None

    model_config = ConfigDict(populate_by_name=True)


class AdminComplaintList(BaseModel):
    items: list[ComplaintRead]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    model_config = ConfigDict(populate_by_name=True)


class CategoryCount(BaseModel):
    category: ComplaintCategory
    count: int

    model_config = ConfigDict(use_enum_values=True)


class DateCount(BaseModel):
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    open_complaints: int = Field(alias="openComplaints")
    high_priority_issues: int = Field(alias="highPriorityIssues")
    resolved_today: int = Field(alias="resolvedToday")
    possible_duplicates: int = Field(alias="possibleDuplicates")
    complaints_by_category: list[CategoryCount] = Field(alias="complaintsByCategory")
    complaints_by_date: list[DateCount] = Field(alias="complaintsByDate")

    model_config = ConfigDict(populate_by_name=True)


class AdminMapPoint(BaseModel):
    reference_id: str = Field(alias="referenceId")
    category: ComplaintCategory
    priority: ComplaintPriority
    status: ComplaintStatus
    latitude: float
    longitude: float
    landmark: str | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)
