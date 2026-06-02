from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.complaint import (
    AnalysisSource,
    ComplaintCategory,
    ComplaintDepartment,
    ComplaintPriority,
    ComplaintStatus,
    SupportedLanguage,
)


Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class ComplaintAnalysisRequest(BaseModel):
    text: Annotated[str, Field(min_length=1)]
    language: SupportedLanguage = SupportedLanguage.en
    photo_url: str | None = Field(default=None, alias="photoUrl")
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    landmark: str | None = None
    category_hint: str | None = Field(default=None, alias="categoryHint")

    model_config = ConfigDict(populate_by_name=True)


class ComplaintAnalysisResponse(BaseModel):
    original_text: str | None = Field(default=None, alias="originalText")
    normalized_english_text: str = Field(alias="normalizedEnglishText")
    original_language: SupportedLanguage | None = Field(default=None, alias="originalLanguage")
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    category: ComplaintCategory
    subcategory: str
    department: ComplaintDepartment | None = None
    priority: ComplaintPriority
    location_text: str | None = Field(alias="locationText")
    missing_fields: list[str] = Field(alias="missingFields")
    follow_up_question: str | None = Field(alias="followUpQuestion")
    citizen_reply: str | None = Field(default=None, alias="citizenReply")
    reasoning_summary: str | None = Field(default=None, alias="reasoningSummary")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    analysis_source: AnalysisSource | None = Field(default=AnalysisSource.FALLBACK_RULES, alias="analysisSource")
    translation_provider: str | None = Field(default=None, alias="translationProvider")
    issue_title: str | None = Field(default=None, alias="issueTitle")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class CoordinatePairMixin(BaseModel):
    latitude: Latitude | None = None
    longitude: Longitude | None = None

    @model_validator(mode="after")
    def validate_coordinate_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class ComplaintCreate(CoordinatePairMixin):
    original_text: Annotated[str, Field(min_length=1)] = Field(alias="originalText")
    normalized_english_text: str | None = Field(default=None, alias="normalizedEnglishText")
    original_language: SupportedLanguage | None = Field(default=None, alias="originalLanguage")
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    category: ComplaintCategory
    subcategory: str | None = None
    department: ComplaintDepartment | None = None
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    landmark: str | None = None
    locality: str | None = None
    ward_name: str | None = Field(default=None, alias="wardName")
    ward_number: int | None = Field(default=None, alias="wardNumber")
    photo_url: str | None = Field(default=None, alias="photoUrl")
    analysis_source: AnalysisSource | None = Field(default=AnalysisSource.FALLBACK_RULES, alias="analysisSource")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    reasoning_summary: str | None = Field(default=None, alias="reasoningSummary")

    model_config = ConfigDict(populate_by_name=True)


class ComplaintResponse(BaseModel):
    reference_id: str = Field(alias="referenceId")
    original_text: str = Field(alias="originalText")
    normalized_english_text: str | None = Field(alias="normalizedEnglishText")
    original_language: SupportedLanguage | None = Field(alias="originalLanguage")
    detected_language: str | None = Field(alias="detectedLanguage")
    category: ComplaintCategory
    subcategory: str | None
    department: ComplaintDepartment | None
    priority: ComplaintPriority
    status: ComplaintStatus
    latitude: float | None
    longitude: float | None
    landmark: str | None
    locality: str | None
    ward_name: str | None = Field(alias="wardName")
    ward_number: int | None = Field(alias="wardNumber")
    photo_url: str | None = Field(alias="photoUrl")
    assigned_team: str | None = Field(alias="assignedTeam")
    internal_note: str | None = Field(alias="internalNote")
    analysis_source: AnalysisSource | None = Field(alias="analysisSource")
    requires_human_verification: bool = Field(alias="requiresHumanVerification")
    reasoning_summary: str | None = Field(alias="reasoningSummary")
    duplicate_of_reference_id: str | None = Field(default=None, alias="duplicateOfReferenceId")
    duplicate_resolution_status: str | None = Field(default=None, alias="duplicateResolutionStatus")
    vision_status: str | None = Field(default=None, alias="visionStatus")
    vision_detected_objects: list[dict] | None = Field(default=None, alias="visionDetectedObjects")
    vision_citizen_message: str | None = Field(default=None, alias="visionCitizenMessage")
    vision_admin_summary: str | None = Field(default=None, alias="visionAdminSummary")
    vision_model_version: str | None = Field(default=None, alias="visionModelVersion")
    vision_processed_at: datetime | None = Field(default=None, alias="visionProcessedAt")
    requires_vision_human_verification: bool = Field(default=True, alias="requiresVisionHumanVerification")
    vision_inference_duration_ms: int | None = Field(default=None, alias="visionInferenceDurationMs")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)


# Backward-compatible alias for the frontend adapter and earlier route code.
ComplaintRead = ComplaintResponse


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus | None = None
    department: ComplaintDepartment | None = None
    priority: ComplaintPriority | None = None
    assigned_team: str | None = Field(default=None, alias="assignedTeam")
    landmark: str | None = None
    locality: str | None = None
    ward_name: str | None = Field(default=None, alias="wardName")
    ward_number: int | None = Field(default=None, alias="wardNumber")
    internal_note: str | None = Field(default=None, alias="internalNote")

    model_config = ConfigDict(populate_by_name=True)


class AdminComplaintList(BaseModel):
    items: list[ComplaintResponse]
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


class LocalityCount(BaseModel):
    locality: str
    count: int


class WardCount(BaseModel):
    ward_number: int | None = Field(alias="wardNumber")
    ward_name: str | None = Field(alias="wardName")
    count: int

    model_config = ConfigDict(populate_by_name=True)


class AdminMapPoint(BaseModel):
    reference_id: str = Field(alias="referenceId")
    category: ComplaintCategory
    priority: ComplaintPriority
    status: ComplaintStatus
    latitude: float
    longitude: float
    landmark: str | None
    locality: str | None
    photo_url: str | None = Field(default=None, alias="photoUrl")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)


class NearbyComplaintResponse(AdminMapPoint):
    distance_meters: float = Field(alias="distanceMeters")


class HotspotResponse(BaseModel):
    locality: str
    category: ComplaintCategory
    complaint_count: int = Field(alias="complaintCount")
    center_latitude: float | None = Field(alias="centerLatitude")
    center_longitude: float | None = Field(alias="centerLongitude")
    radius_meters: int = Field(alias="radiusMeters")
    latest_complaint_at: datetime = Field(alias="latestComplaintAt")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class AnalyticsResponse(BaseModel):
    open_complaints: int = Field(alias="openComplaints")
    high_priority_issues: int = Field(alias="highPriorityIssues")
    resolved_today: int = Field(alias="resolvedToday")
    possible_duplicates: int = Field(default=0, alias="possibleDuplicates")
    confirmed_duplicates: int = Field(default=0, alias="confirmedDuplicates")
    rejected_duplicate_suggestions: int = Field(default=0, alias="rejectedDuplicateSuggestions")
    pending_duplicate_reviews: int = Field(default=0, alias="pendingDuplicateReviews")
    complaints_by_category: list[CategoryCount] = Field(alias="complaintsByCategory")
    complaints_by_date: list[DateCount] = Field(alias="complaintsByDate")
    complaints_by_locality: list[LocalityCount] = Field(alias="complaintsByLocality")
    complaints_by_ward: list[WardCount] = Field(alias="complaintsByWard")
    hotspots: list[HotspotResponse]

    model_config = ConfigDict(populate_by_name=True)
