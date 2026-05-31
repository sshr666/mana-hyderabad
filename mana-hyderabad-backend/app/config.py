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


@lru_cache
def get_settings() -> Settings:
    return Settings()
