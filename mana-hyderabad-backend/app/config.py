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
    enable_llm_analysis: bool = Field(default=True, alias="ENABLE_LLM_ANALYSIS")
    llm_provider: str = Field(default="openai_compatible", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    llm_model: str = Field(default="", alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=20, alias="LLM_TIMEOUT_SECONDS")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")
    llm_temperature: float = Field(default=0, alias="LLM_TEMPERATURE")
    llm_max_output_tokens: int = Field(default=800, alias="LLM_MAX_OUTPUT_TOKENS")
    enable_rule_fallback: bool = Field(default=True, alias="ENABLE_RULE_FALLBACK")
    enable_llm_json_mode: bool = Field(default=True, alias="ENABLE_LLM_JSON_MODE")
    enable_duplicate_detection: bool = Field(default=True, alias="ENABLE_DUPLICATE_DETECTION")
    duplicate_radius_meters: int = Field(default=200, alias="DUPLICATE_RADIUS_METERS")
    duplicate_time_window_hours: int = Field(default=72, alias="DUPLICATE_TIME_WINDOW_HOURS")
    duplicate_min_semantic_similarity: float = Field(default=0.78, alias="DUPLICATE_MIN_SEMANTIC_SIMILARITY")
    duplicate_high_similarity_threshold: float = Field(default=0.88, alias="DUPLICATE_HIGH_SIMILARITY_THRESHOLD")
    duplicate_max_candidates: int = Field(default=20, alias="DUPLICATE_MAX_CANDIDATES")
    store_low_confidence_duplicates: bool = Field(default=False, alias="STORE_LOW_CONFIDENCE_DUPLICATES")
    embedding_provider: str = Field(default="openai_compatible", alias="EMBEDDING_PROVIDER")
    embedding_api_key: str = Field(default="", alias="EMBEDDING_API_KEY")
    embedding_base_url: str = Field(default="", alias="EMBEDDING_BASE_URL")
    embedding_model: str = Field(default="", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")
    embedding_timeout_seconds: int = Field(default=20, alias="EMBEDDING_TIMEOUT_SECONDS")
    embedding_max_retries: int = Field(default=2, alias="EMBEDDING_MAX_RETRIES")
    enable_embedding_fallback: bool = Field(default=False, alias="ENABLE_EMBEDDING_FALLBACK")
    enable_vision_analysis: bool = Field(default=True, alias="ENABLE_VISION_ANALYSIS")
    vision_model_path: str = Field(default="cv/models/best.pt", alias="VISION_MODEL_PATH")
    vision_base_model: str = Field(default="", alias="VISION_BASE_MODEL")
    vision_confidence_threshold: float = Field(default=0.45, alias="VISION_CONFIDENCE_THRESHOLD")
    vision_iou_threshold: float = Field(default=0.50, alias="VISION_IOU_THRESHOLD")
    vision_max_image_size_mb: int = Field(default=8, alias="VISION_MAX_IMAGE_SIZE_MB")
    vision_image_download_timeout_seconds: int = Field(default=15, alias="VISION_IMAGE_DOWNLOAD_TIMEOUT_SECONDS")
    vision_allowed_image_hosts: str = Field(default="", alias="VISION_ALLOWED_IMAGE_HOSTS")
    vision_store_bounding_boxes: bool = Field(default=True, alias="VISION_STORE_BOUNDING_BOXES")
    vision_run_on_complaint_submission: bool = Field(default=True, alias="VISION_RUN_ON_COMPLAINT_SUBMISSION")
    vision_device: str = Field(default="auto", alias="VISION_DEVICE")
    vision_image_size: int = Field(default=640, alias="VISION_IMAGE_SIZE")
    vision_max_detections: int = Field(default=20, alias="VISION_MAX_DETECTIONS")
    vision_model_version: str = Field(default="mana-hyderabad-civic-v1", alias="VISION_MODEL_VERSION")

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

    @property
    def vision_max_image_size_bytes(self) -> int:
        return self.vision_max_image_size_mb * 1024 * 1024

    @property
    def trusted_vision_image_hosts(self) -> set[str]:
        return {item.strip().lower() for item in self.vision_allowed_image_hosts.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
