from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.vision import (
    ComplaintVisionAnalysisResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
    VisionHealthResponse,
)
from app.services.vision_analysis_service import (
    analyse_complaint_image,
    analyse_photo_url,
    get_stored_complaint_vision_analysis,
    run_complaint_vision_analysis,
    vision_health,
)

router = APIRouter(tags=["vision"])


@router.get("/api/vision/health", response_model=VisionHealthResponse)
def get_vision_health() -> VisionHealthResponse:
    return vision_health()


@router.post("/api/vision/analyse", response_model=VisionAnalysisResponse)
async def analyse_image(payload: VisionAnalysisRequest) -> VisionAnalysisResponse:
    if payload.photo_url:
        return await analyse_photo_url(str(payload.photo_url))
    raise HTTPException(status.HTTP_400_BAD_REQUEST, "photoUrl is required for direct image analysis.")


@router.post(
    "/api/admin/complaints/{reference_id}/run-vision-analysis",
    response_model=ComplaintVisionAnalysisResponse,
)
async def run_admin_vision_analysis(
    reference_id: str,
    db: Session = Depends(get_db),
) -> ComplaintVisionAnalysisResponse:
    return await analyse_complaint_image(db, reference_id)


@router.get(
    "/api/admin/complaints/{reference_id}/vision-analysis",
    response_model=ComplaintVisionAnalysisResponse,
)
def get_admin_vision_analysis(
    reference_id: str,
    db: Session = Depends(get_db),
) -> ComplaintVisionAnalysisResponse:
    return get_stored_complaint_vision_analysis(db, reference_id)


def schedule_vision_analysis(background_tasks: BackgroundTasks, reference_id: str) -> None:
    background_tasks.add_task(run_complaint_vision_analysis, reference_id)
