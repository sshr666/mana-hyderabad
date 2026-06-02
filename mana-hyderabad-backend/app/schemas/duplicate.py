from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.complaint import (
    ComplaintCategory,
    ComplaintStatus,
    DuplicateConfidence,
    DuplicateSuggestionStatus,
)


class DuplicateSuggestionResponse(BaseModel):
    suggestion_id: UUID = Field(alias="suggestionId")
    source_reference_id: str = Field(alias="sourceReferenceId")
    candidate_reference_id: str = Field(alias="candidateReferenceId")
    candidate_category: ComplaintCategory = Field(alias="candidateCategory")
    candidate_status: ComplaintStatus = Field(alias="candidateStatus")
    candidate_landmark: str | None = Field(alias="candidateLandmark")
    distance_meters: float = Field(alias="distanceMeters")
    time_difference_hours: float = Field(alias="timeDifferenceHours")
    semantic_similarity: float | None = Field(alias="semanticSimilarity")
    duplicate_score: float = Field(alias="duplicateScore")
    confidence_label: DuplicateConfidence = Field(alias="confidenceLabel")
    status: DuplicateSuggestionStatus
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class DuplicateReviewPayload(BaseModel):
    reviewed_by: str = Field(default="admin", alias="reviewedBy", min_length=1, max_length=120)
    review_note: str | None = Field(default=None, alias="reviewNote", max_length=1000)

    model_config = ConfigDict(populate_by_name=True)


class DuplicateReviewResponse(BaseModel):
    suggestion: DuplicateSuggestionResponse
    source_reference_id: str = Field(alias="sourceReferenceId")
    candidate_reference_id: str = Field(alias="candidateReferenceId")
    status: DuplicateSuggestionStatus
    message: str

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class EmbeddingResult(BaseModel):
    embedding: list[float]
    source_text: str = Field(alias="sourceText")
    provider: str
    model: str
    dimensions: int

    model_config = ConfigDict(populate_by_name=True)
