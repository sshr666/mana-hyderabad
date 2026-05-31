from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SupportedTranslationLanguage = Literal["en", "te", "hi", "ur"]
TranslationAnalysisSource = Literal["RULES", "BHASHINI", "FALLBACK"]


TrimmedText = Annotated[str, Field(min_length=1, max_length=5000)]


class DetectLanguageRequest(BaseModel):
    text: TrimmedText

    @field_validator("text")
    @classmethod
    def trim_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty")
        return stripped


class DetectLanguageResponse(BaseModel):
    detected_language: str = Field(alias="detectedLanguage")
    confidence: float | None = None
    is_mixed_language: bool = Field(alias="isMixedLanguage")
    detected_scripts: list[str] = Field(alias="detectedScripts")
    analysis_source: TranslationAnalysisSource = Field(alias="analysisSource")

    model_config = ConfigDict(populate_by_name=True)


class TranslationRequest(BaseModel):
    text: TrimmedText
    source_language: str | None = Field(default=None, alias="sourceLanguage")
    target_language: SupportedTranslationLanguage = Field(alias="targetLanguage")
    preserve_terms: list[str] | None = Field(default=None, alias="preserveTerms")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("text")
    @classmethod
    def trim_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty")
        return stripped


class TranslationResponse(BaseModel):
    original_text: str = Field(alias="originalText")
    translated_text: str = Field(alias="translatedText")
    source_language: str = Field(alias="sourceLanguage")
    target_language: str = Field(alias="targetLanguage")
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    is_mixed_language: bool = Field(alias="isMixedLanguage")
    provider: str
    preserved_terms: list[str] = Field(default_factory=list, alias="preservedTerms")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")

    model_config = ConfigDict(populate_by_name=True)


class NormalizedComplaintText(BaseModel):
    original_text: str = Field(alias="originalText")
    original_language: str = Field(alias="originalLanguage")
    detected_language: str = Field(alias="detectedLanguage")
    normalized_english_text: str = Field(alias="normalizedEnglishText")
    is_mixed_language: bool = Field(alias="isMixedLanguage")
    provider: str
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")

    model_config = ConfigDict(populate_by_name=True)
