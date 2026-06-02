from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SupportedSpeechLanguage = Literal["en", "te", "hi", "ur"]


class SpeechTranscriptionResponse(BaseModel):
    transcript: str
    detected_language: str | None = Field(default=None, alias="detectedLanguage")
    requested_language: str = Field(alias="requestedLanguage")
    provider: str
    audio_duration_seconds: float | None = Field(default=None, alias="audioDurationSeconds")
    requires_human_verification: bool = Field(default=True, alias="requiresHumanVerification")
    fallback_used: bool = Field(default=False, alias="fallbackUsed")

    model_config = ConfigDict(populate_by_name=True)


class SpeechSynthesisRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=1000)]
    language: SupportedSpeechLanguage

    @field_validator("text")
    @classmethod
    def trim_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be empty")
        return stripped


class SpeechSynthesisResponse(BaseModel):
    audio_base64: str | None = Field(default=None, alias="audioBase64")
    audio_url: str | None = Field(default=None, alias="audioUrl")
    language: str
    provider: str
    format: str
    fallback_used: bool = Field(default=False, alias="fallbackUsed")

    model_config = ConfigDict(populate_by_name=True)
