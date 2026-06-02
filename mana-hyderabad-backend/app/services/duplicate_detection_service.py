import math
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.complaint import (
    Complaint,
    ComplaintDuplicateSuggestion,
    DuplicateConfidence,
    DuplicateResolutionStatus,
    DuplicateSuggestionStatus,
)
from app.repositories import complaint_repository
from app.schemas.duplicate import (
    DuplicateReviewPayload,
    DuplicateReviewResponse,
    DuplicateSuggestionResponse,
)
from app.services.embedding_service import generate_complaint_embedding_sync


def try_generate_and_store_embedding(db: Session, complaint: Complaint) -> bool:
    settings = get_settings()
    normalized_text = complaint.normalized_english_text or complaint.original_text
    try:
        result = generate_complaint_embedding_sync(
            normalized_english_text=normalized_text,
            category=complaint.category.value,
            landmark=complaint.landmark,
            locality=complaint.locality,
        )
        complaint_repository.update_embedding(
            db,
            complaint,
            embedding=result.embedding,
            source_text=result.source_text,
        )
        db.commit()
        db.refresh(complaint)
        return True
    except Exception:
        db.rollback()
        return False if not settings.enable_embedding_fallback else False


def detect_duplicate_candidates(db: Session, complaint_id: UUID) -> list[DuplicateSuggestionResponse]:
    settings = get_settings()
    if not settings.enable_duplicate_detection:
        return []
    source = complaint_repository.get_by_id(db, complaint_id)
    if source is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Complaint was not found.")
    if source.location is None:
        return []
    if source.embedding is None:
        try_generate_and_store_embedding(db, source)
    candidates = complaint_repository.get_duplicate_candidates(
        db,
        source=source,
        radius_meters=settings.duplicate_radius_meters,
        time_window_hours=settings.duplicate_time_window_hours,
        max_candidates=settings.duplicate_max_candidates,
    )
    suggestions: list[ComplaintDuplicateSuggestion] = []
    for candidate, distance_meters, time_difference_hours in candidates:
        similarity = cosine_similarity(source.embedding, candidate.embedding)
        if candidate.embedding is None:
            similarity = None
        score = calculate_duplicate_score(
            semantic_similarity=similarity,
            distance_meters=distance_meters,
            radius_meters=settings.duplicate_radius_meters,
            time_difference_hours=time_difference_hours,
            time_window_hours=settings.duplicate_time_window_hours,
            category_match=True,
        )
        confidence = confidence_label(
            duplicate_score=score,
            semantic_similarity=similarity,
            min_similarity=settings.duplicate_min_semantic_similarity,
            high_similarity=settings.duplicate_high_similarity_threshold,
        )
        if confidence == DuplicateConfidence.LOW and not settings.store_low_confidence_duplicates:
            continue
        suggestion = ComplaintDuplicateSuggestion(
            source_complaint_id=source.id,
            candidate_complaint_id=candidate.id,
            distance_meters=distance_meters,
            time_difference_hours=time_difference_hours,
            semantic_similarity=similarity,
            category_match=True,
            duplicate_score=score,
            confidence_label=confidence,
            status=DuplicateSuggestionStatus.PENDING_REVIEW,
        )
        suggestions.append(complaint_repository.upsert_duplicate_suggestion(db, suggestion))
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Could not store duplicate suggestions.") from exc
    return [to_duplicate_response(item, source, complaint_repository.get_by_id(db, item.candidate_complaint_id)) for item in suggestions]


def get_duplicate_suggestions(db: Session, reference_id: str) -> list[DuplicateSuggestionResponse]:
    rows = complaint_repository.get_duplicate_suggestions_for_reference(db, reference_id)
    return [to_duplicate_response(suggestion, source, candidate) for suggestion, source, candidate in rows]


def confirm_duplicate(
    db: Session,
    suggestion_id: UUID,
    payload: DuplicateReviewPayload,
) -> DuplicateReviewResponse:
    suggestion, source, candidate = _get_suggestion_or_404(db, suggestion_id)
    suggestion.status = DuplicateSuggestionStatus.CONFIRMED_DUPLICATE
    suggestion.reviewed_by = payload.reviewed_by
    suggestion.reviewed_at = datetime.now(timezone.utc)
    suggestion.review_note = payload.review_note
    source.duplicate_of_reference_id = candidate.reference_id
    source.duplicate_resolution_status = DuplicateResolutionStatus.CONFIRMED_DUPLICATE
    db.commit()
    db.refresh(suggestion)
    db.refresh(source)
    return DuplicateReviewResponse(
        suggestion=to_duplicate_response(suggestion, source, candidate),
        sourceReferenceId=source.reference_id,
        candidateReferenceId=candidate.reference_id,
        status=suggestion.status,
        message="Duplicate relationship confirmed. The original complaint remains stored and traceable.",
    )


def reject_duplicate(
    db: Session,
    suggestion_id: UUID,
    payload: DuplicateReviewPayload,
) -> DuplicateReviewResponse:
    suggestion, source, candidate = _get_suggestion_or_404(db, suggestion_id)
    suggestion.status = DuplicateSuggestionStatus.REJECTED
    suggestion.reviewed_by = payload.reviewed_by
    suggestion.reviewed_at = datetime.now(timezone.utc)
    suggestion.review_note = payload.review_note
    source.duplicate_resolution_status = DuplicateResolutionStatus.KEEP_SEPARATE
    db.commit()
    db.refresh(suggestion)
    db.refresh(source)
    return DuplicateReviewResponse(
        suggestion=to_duplicate_response(suggestion, source, candidate),
        sourceReferenceId=source.reference_id,
        candidateReferenceId=candidate.reference_id,
        status=suggestion.status,
        message="Complaints kept separate for municipal review.",
    )


def calculate_duplicate_score(
    *,
    semantic_similarity: float | None,
    distance_meters: float,
    radius_meters: int,
    time_difference_hours: float,
    time_window_hours: int,
    category_match: bool,
) -> float:
    distance_score = max(0.0, 1.0 - (distance_meters / max(radius_meters, 1)))
    time_score = max(0.0, 1.0 - (time_difference_hours / max(time_window_hours, 1)))
    category_score = 1.0 if category_match else 0.0
    if semantic_similarity is None:
        score = 0.55 * distance_score + 0.35 * time_score + 0.10 * category_score
    else:
        score = (
            0.55 * max(0.0, min(1.0, semantic_similarity))
            + 0.25 * distance_score
            + 0.15 * time_score
            + 0.05 * category_score
        )
    return round(max(0.0, min(1.0, score)), 4)


def confidence_label(
    *,
    duplicate_score: float,
    semantic_similarity: float | None,
    min_similarity: float,
    high_similarity: float,
) -> DuplicateConfidence:
    if duplicate_score >= 0.85 and (semantic_similarity is None or semantic_similarity >= high_similarity):
        return DuplicateConfidence.HIGH
    if duplicate_score >= 0.65 and (semantic_similarity is None or semantic_similarity >= min_similarity):
        return DuplicateConfidence.MEDIUM
    return DuplicateConfidence.LOW


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float | None:
    if not left or not right or len(left) != len(right):
        return None
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return None
    return max(-1.0, min(1.0, dot / (left_norm * right_norm)))


def to_duplicate_response(
    suggestion: ComplaintDuplicateSuggestion,
    source: Complaint,
    candidate: Complaint | None,
) -> DuplicateSuggestionResponse:
    if candidate is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Duplicate candidate complaint was not found.")
    return DuplicateSuggestionResponse(
        suggestionId=suggestion.id,
        sourceReferenceId=source.reference_id,
        candidateReferenceId=candidate.reference_id,
        candidateCategory=candidate.category,
        candidateStatus=candidate.status,
        candidateLandmark=candidate.landmark,
        distanceMeters=round(suggestion.distance_meters, 2),
        timeDifferenceHours=round(suggestion.time_difference_hours, 2),
        semanticSimilarity=round(suggestion.semantic_similarity, 4)
        if suggestion.semantic_similarity is not None
        else None,
        duplicateScore=round(suggestion.duplicate_score, 4),
        confidenceLabel=suggestion.confidence_label,
        status=suggestion.status,
        createdAt=suggestion.created_at,
    )


def _get_suggestion_or_404(
    db: Session,
    suggestion_id: UUID,
) -> tuple[ComplaintDuplicateSuggestion, Complaint, Complaint]:
    row = complaint_repository.get_duplicate_suggestion(db, suggestion_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Duplicate suggestion was not found.")
    return row
