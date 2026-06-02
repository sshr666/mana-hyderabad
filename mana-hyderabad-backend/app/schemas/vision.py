from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models.complaint import VisionStatus


CivicVisionLabel = Literal["garbage_heap", "blocked_drain", "stagnant_water", "pothole"]


class BoundingBox(BaseModel):
    x_min: Annotated[float, Field(ge=0, alias="xMin")]
    y_min: Annotated[float, Field(ge=0, alias="yMin")]
    x_max: Annotated[float, Field(alias="xMax")]
    y_max: Annotated[float, Field(alias="yMax")]

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.x_max <= self.x_min:
            raise ValueError("xMax must be greater than xMin")
        if self.y_max <= self.y_min:
            raise ValueError("yMax must be greater than yMin")
        return self


class DetectedObject(BaseModel):
    label: CivicVisionLabel
    confidence: Annotated[float, Field(ge=0, le=1)]
    bounding_box: BoundingBox | None = Field(default=None, alias="boundingBox")

    model_config = ConfigDict(populate_by_name=True)


class VisionAnalysisRequest(BaseModel):
    photo_url: HttpUrl | None = Field(default=None, alias="photoUrl")
    complaint_reference_id: str | None = Field(default=None, alias="complaintReferenceId")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def require_reference_or_url(self):
        if self.photo_url is None and not self.complaint_reference_id:
            raise ValueError("photoUrl or complaintReferenceId is required")
        return self


class VisionAnalysisResponse(BaseModel):
    status: VisionStatus
    detected_objects: list[DetectedObject] = Field(alias="detectedObjects")
    citizen_message: str = Field(alias="citizenMessage")
    admin_summary: str = Field(alias="adminSummary")
    model_version: str | None = Field(default=None, alias="modelVersion")
    processed_at: datetime | None = Field(default=None, alias="processedAt")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    inference_duration_ms: int | None = Field(default=None, alias="inferenceDurationMs")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class ComplaintVisionAnalysisResponse(BaseModel):
    complaint_reference_id: str = Field(alias="complaintReferenceId")
    vision_status: VisionStatus = Field(alias="visionStatus")
    detected_objects: list[DetectedObject] = Field(alias="detectedObjects")
    citizen_message: str | None = Field(default=None, alias="citizenMessage")
    admin_summary: str | None = Field(default=None, alias="adminSummary")
    model_version: str | None = Field(default=None, alias="modelVersion")
    processed_at: datetime | None = Field(default=None, alias="processedAt")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    inference_duration_ms: int | None = Field(default=None, alias="inferenceDurationMs")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class VisionHealthResponse(BaseModel):
    status: str
    enabled: bool
    model_configured: bool = Field(alias="modelConfigured")
    model_loaded: bool = Field(alias="modelLoaded")
    model_version: str | None = Field(alias="modelVersion")
    device: str

    model_config = ConfigDict(populate_by_name=True)
