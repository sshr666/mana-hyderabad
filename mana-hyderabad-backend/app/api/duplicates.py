from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.duplicate import DuplicateReviewPayload, DuplicateReviewResponse, DuplicateSuggestionResponse
from app.services.complaint_service import get_complaint_by_reference
from app.services.duplicate_detection_service import (
    confirm_duplicate,
    detect_duplicate_candidates,
    get_duplicate_suggestions,
    reject_duplicate,
)

router = APIRouter(prefix="/api/admin", tags=["duplicates"])


@router.get("/complaints/{reference_id}/duplicate-suggestions", response_model=list[DuplicateSuggestionResponse])
def list_duplicate_suggestions(reference_id: str, db: Session = Depends(get_db)) -> list[DuplicateSuggestionResponse]:
    get_complaint_by_reference(db, reference_id)
    return get_duplicate_suggestions(db, reference_id)


@router.post("/complaints/{reference_id}/run-duplicate-check", response_model=list[DuplicateSuggestionResponse])
def run_duplicate_check(reference_id: str, db: Session = Depends(get_db)) -> list[DuplicateSuggestionResponse]:
    complaint = get_complaint_by_reference(db, reference_id)
    return detect_duplicate_candidates(db, complaint.id)


@router.post("/duplicate-suggestions/{suggestion_id}/confirm", response_model=DuplicateReviewResponse)
def confirm_duplicate_suggestion(
    suggestion_id: UUID,
    payload: DuplicateReviewPayload,
    db: Session = Depends(get_db),
) -> DuplicateReviewResponse:
    return confirm_duplicate(db, suggestion_id, payload)


@router.post("/duplicate-suggestions/{suggestion_id}/reject", response_model=DuplicateReviewResponse)
def reject_duplicate_suggestion(
    suggestion_id: UUID,
    payload: DuplicateReviewPayload,
    db: Session = Depends(get_db),
) -> DuplicateReviewResponse:
    return reject_duplicate(db, suggestion_id, payload)
