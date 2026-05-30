from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.complaint import (
    ComplaintAnalysisRequest,
    ComplaintAnalysisResponse,
    ComplaintCreate,
    ComplaintCreateResponse,
    ComplaintRead,
)
from app.services.analysis_service import analyse_complaint
from app.services.complaint_service import create_complaint, get_complaint_by_reference

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/analyse", response_model=ComplaintAnalysisResponse)
def analyse(payload: ComplaintAnalysisRequest) -> ComplaintAnalysisResponse:
    return analyse_complaint(payload)


@router.post("", response_model=ComplaintCreateResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)) -> ComplaintCreateResponse:
    complaint = create_complaint(db, payload)
    return ComplaintCreateResponse(
        referenceId=complaint.reference_id,
        status="SUBMITTED",
        createdAt=complaint.created_at,
    )


@router.get("/{reference_id}", response_model=ComplaintRead)
def track_complaint(reference_id: str, db: Session = Depends(get_db)) -> ComplaintRead:
    return get_complaint_by_reference(db, reference_id)
