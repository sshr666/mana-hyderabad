from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/mana_hyderabad",
        alias="DATABASE_URL",
    )
    frontend_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="FRONTEND_ORIGINS",
    )
    cloudinary_cloud_name: str = Field(default="", alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(default="", alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(default="", alias="CLOUDINARY_API_SECRET")
    cloudinary_upload_folder: str = Field(default="mana-hyderabad/complaints", alias="CLOUDINARY_UPLOAD_FOLDER")
    max_upload_size_mb: int = Field(default=8, alias="MAX_UPLOAD_SIZE_MB")
    allowed_image_types: str = Field(default="image/jpeg,image/png,image/webp", alias="ALLOWED_IMAGE_TYPES")
    translation_provider: str = Field(default="bhashini", alias="TRANSLATION_PROVIDER")
    enable_translation: bool = Field(default=True, alias="ENABLE_TRANSLATION")
    translation_timeout_seconds: int = Field(default=20, alias="TRANSLATION_TIMEOUT_SECONDS")
    translation_max_retries: int = Field(default=2, alias="TRANSLATION_MAX_RETRIES")
    bhashini_user_id: str = Field(default="", alias="BHASHINI_USER_ID")
    bhashini_api_key: str = Field(default="", alias="BHASHINI_API_KEY")
    bhashini_pipeline_id: str = Field(default="", alias="BHASHINI_PIPELINE_ID")
    bhashini_config_url: str = Field(default="", alias="BHASHINI_CONFIG_URL")
    bhashini_cache_ttl_seconds: int = Field(default=3600, alias="BHASHINI_CACHE_TTL_SECONDS")
    enable_indic_trans2_fallback: bool = Field(default=False, alias="ENABLE_INDIC_TRANS2_FALLBACK")
    indic_trans2_base_url: str = Field(default="", alias="INDIC_TRANS2_BASE_URL")
    indic_trans2_timeout_seconds: int = Field(default=30, alias="INDIC_TRANS2_TIMEOUT_SECONDS")
    enable_speech_input: bool = Field(default=True, alias="ENABLE_SPEECH_INPUT")
    enable_tts_responses: bool = Field(default=False, alias="ENABLE_TTS_RESPONSES")
    bhashini_asr_pipeline_id: str = Field(default="", alias="BHASHINI_ASR_PIPELINE_ID")
    bhashini_tts_pipeline_id: str = Field(default="", alias="BHASHINI_TTS_PIPELINE_ID")
    bhashini_speech_config_url: str = Field(default="", alias="BHASHINI_SPEECH_CONFIG_URL")
    bhashini_speech_timeout_seconds: int = Field(default=30, alias="BHASHINI_SPEECH_TIMEOUT_SECONDS")
    bhashini_speech_max_retries: int = Field(default=2, alias="BHASHINI_SPEECH_MAX_RETRIES")
    bhashini_speech_cache_ttl_seconds: int = Field(default=3600, alias="BHASHINI_SPEECH_CACHE_TTL_SECONDS")
    max_audio_size_mb: int = Field(default=10, alias="MAX_AUDIO_SIZE_MB")
    max_audio_duration_seconds: int = Field(default=120, alias="MAX_AUDIO_DURATION_SECONDS")
    allowed_audio_types: str = Field(
        default="audio/webm,audio/wav,audio/mpeg,audio/mp4,audio/ogg",
        alias="ALLOWED_AUDIO_TYPES",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> List[str]:
        raw = self.frontend_origins.strip()
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def allowed_image_mime_types(self) -> set[str]:
        return {item.strip() for item in self.allowed_image_types.split(",") if item.strip()}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_audio_mime_types(self) -> set[str]:
        return {item.strip() for item in self.allowed_audio_types.split(",") if item.strip()}

    @property
    def max_audio_size_bytes(self) -> int:
        return self.max_audio_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
