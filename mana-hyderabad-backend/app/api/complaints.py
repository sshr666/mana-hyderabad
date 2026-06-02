from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.analysis import ComplaintAnalysisRequest, ComplaintAnalysisResponse
from app.database import get_db
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
)
from app.services.analysis_service import analyse_complaint
from app.services.complaint_service import create_complaint, get_complaint_by_reference

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/analyse", response_model=ComplaintAnalysisResponse)
async def analyse(payload: ComplaintAnalysisRequest) -> ComplaintAnalysisResponse:
    return await analyse_complaint(payload)


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)) -> ComplaintResponse:
    return create_complaint(db, payload)


@router.get("/{reference_id}", response_model=ComplaintResponse)
def track_complaint(reference_id: str, db: Session = Depends(get_db)) -> ComplaintResponse:
    return get_complaint_by_reference(db, reference_id)
