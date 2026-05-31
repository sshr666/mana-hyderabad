from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel, Field

from app.services.file_upload_service import delete_temporary_image, upload_complaint_image


router = APIRouter(prefix="/api/uploads", tags=["uploads"])


class UploadedImageResponse(BaseModel):
    photo_url: str = Field(alias="photoUrl")
    public_id: str = Field(alias="publicId")
    width: int | None = None
    height: int | None = None
    format: str | None = None
    bytes: int | None = None


class DeleteImageRequest(BaseModel):
    public_id: str = Field(alias="publicId")


class DeleteImageResponse(BaseModel):
    public_id: str = Field(alias="publicId")
    deleted: bool


@router.post("/images", response_model=UploadedImageResponse)
async def upload_image(file: UploadFile = File(...)) -> UploadedImageResponse:
    result = await upload_complaint_image(file)
    return UploadedImageResponse(
        photoUrl=result.secure_url,
        publicId=result.public_id,
        width=result.width,
        height=result.height,
        format=result.format,
        bytes=result.bytes,
    )


@router.delete("/images", response_model=DeleteImageResponse)
def delete_image(payload: DeleteImageRequest) -> DeleteImageResponse:
    result = delete_temporary_image(payload.public_id)
    return DeleteImageResponse(publicId=result.public_id, deleted=result.deleted)
