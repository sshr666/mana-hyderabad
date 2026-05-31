import io
import uuid
from pathlib import Path

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from app.config import get_settings


class UploadedImageResult(BaseModel):
    secure_url: str = Field(alias="secureUrl")
    public_id: str = Field(alias="publicId")
    width: int | None = None
    height: int | None = None
    format: str | None = None
    bytes: int | None = None


class DeleteImageResult(BaseModel):
    public_id: str = Field(alias="publicId")
    deleted: bool


ALLOWED_EXTENSIONS = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}


async def upload_complaint_image(file: UploadFile | None) -> UploadedImageResult:
    settings = get_settings()
    if file is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Image file is required.")
    if not file.filename:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Image filename is required.")

    content_type = file.content_type or ""
    if content_type not in settings.allowed_image_mime_types:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported image type. Upload JPEG, PNG, or WEBP.")
    extension = Path(file.filename).suffix.lower()
    if extension and extension not in ALLOWED_EXTENSIONS.get(content_type, set()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported image extension. Upload JPEG, PNG, or WEBP.")

    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded image is empty.")
    if len(data) > settings.max_upload_size_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Image must be smaller than {settings.max_upload_size_mb} MB.")

    width, height, image_format = _inspect_image(data, content_type)
    _configure_cloudinary()
    public_id = f"{settings.cloudinary_upload_folder.rstrip('/')}/{uuid.uuid4().hex}"
    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(data),
            public_id=public_id,
            resource_type="image",
            folder=None,
            overwrite=False,
            unique_filename=False,
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not upload image. Please try again.") from exc

    secure_url = result.get("secure_url")
    returned_public_id = result.get("public_id")
    if not isinstance(secure_url, str) or not secure_url.startswith("https://") or not isinstance(returned_public_id, str):
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Cloudinary did not return a valid secure image URL.")

    return UploadedImageResult(
        secureUrl=secure_url,
        publicId=returned_public_id,
        width=_int_or_none(result.get("width")) or width,
        height=_int_or_none(result.get("height")) or height,
        format=str(result.get("format") or image_format).lower(),
        bytes=_int_or_none(result.get("bytes")) or len(data),
    )


def delete_temporary_image(public_id: str) -> DeleteImageResult:
    if not public_id.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "publicId is required.")
    _configure_cloudinary()
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not delete image. Please try again.") from exc
    return DeleteImageResult(publicId=public_id, deleted=result.get("result") in {"ok", "not found"})


def _inspect_image(data: bytes, content_type: str) -> tuple[int | None, int | None, str | None]:
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image_format = (image.format or "").upper()
            if content_type == "image/jpeg" and image_format != "JPEG":
                raise ValueError
            if content_type == "image/png" and image_format != "PNG":
                raise ValueError
            if content_type == "image/webp" and image_format != "WEBP":
                raise ValueError
            return image.width, image.height, image_format.lower()
    except (UnidentifiedImageError, ValueError, OSError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Malformed image. Upload a valid JPEG, PNG, or WEBP file.") from exc


def _configure_cloudinary() -> None:
    settings = get_settings()
    if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key or not settings.cloudinary_api_secret:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Cloudinary is not configured on the backend.")
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def _int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None
