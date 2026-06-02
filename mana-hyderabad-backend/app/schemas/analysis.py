from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.complaint import ComplaintCategory, ComplaintDepartment, ComplaintPriority


AnalysisSourceValue = Literal["LLM", "FALLBACK_RULES", "LLM_WITH_GUARDRAILS"]


class ComplaintAnalysisRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=5000)]
    normalized_english_text: str | None = Field(default=None, alias="normalizedEnglishText")
    original_language: str | None = Field(default=None, alias="originalLanguage")
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    language: str | None = None
    latitude: Annotated[float, Field(ge=-90, le=90)] | None = None
    longitude: Annotated[float, Field(ge=-180, le=180)] | None = None
    landmark: str | None = None
    photo_url: str | None = Field(default=None, alias="photoUrl")
    category_hint: str | None = Field(default=None, alias="categoryHint")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("text")
    @classmethod
    def trim_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty")
        return stripped

    @model_validator(mode="after")
    def validate_coordinate_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class LLMComplaintAnalysis(BaseModel):
    category: ComplaintCategory
    subcategory: Annotated[str, Field(min_length=1, max_length=96)]
    department: ComplaintDepartment
    priority: ComplaintPriority
    location_text: str | None = Field(default=None, alias="locationText")
    missing_fields: list[str] = Field(default_factory=list, alias="missingFields")
    follow_up_question: str | None = Field(default=None, alias="followUpQuestion")
    citizen_reply: Annotated[str, Field(min_length=1, max_length=500)] = Field(alias="citizenReply")
    admin_summary: Annotated[str, Field(min_length=1, max_length=800)] = Field(alias="adminSummary")
    reasoning_summary: Annotated[str, Field(min_length=1, max_length=500)] = Field(alias="reasoningSummary")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class ComplaintAnalysisResponse(LLMComplaintAnalysis):
    original_text: str = Field(alias="originalText")
    normalized_english_text: str = Field(alias="normalizedEnglishText")
    original_language: str | None = Field(default=None, alias="originalLanguage")
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    analysis_source: AnalysisSourceValue = Field(alias="analysisSource")
    translation_provider: str | None = Field(default=None, alias="translationProvider")
    issue_title: str | None = Field(default=None, alias="issueTitle")
    guardrails_applied: list[str] = Field(default_factory=list, alias="guardrailsApplied")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
