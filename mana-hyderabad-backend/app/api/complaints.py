from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.schemas.analysis import ComplaintAnalysisRequest, ComplaintAnalysisResponse
from app.database import get_db
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
)
from app.services.analysis_service import analyse_complaint
from app.services.complaint_service import create_complaint, get_complaint_by_reference
from app.api.vision import schedule_vision_analysis
from app.config import get_settings

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/analyse", response_model=ComplaintAnalysisResponse)
async def analyse(payload: ComplaintAnalysisRequest) -> ComplaintAnalysisResponse:
    return await analyse_complaint(payload)


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(
    payload: ComplaintCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    complaint = create_complaint(db, payload)
    settings = get_settings()
    if settings.enable_vision_analysis and settings.vision_run_on_complaint_submission and complaint.photo_url:
        # TODO: Move vision processing to a durable queue when production workloads require retries.
        schedule_vision_analysis(background_tasks, complaint.reference_id)
    return complaint


@router.get("/{reference_id}", response_model=ComplaintResponse)
def track_complaint(reference_id: str, db: Session = Depends(get_db)) -> ComplaintResponse:
    return get_complaint_by_reference(db, reference_id)
