from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintCategory, ComplaintDepartment, ComplaintStatus
from app.repositories import complaint_repository
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate


CATEGORY_PREFIXES: dict[ComplaintCategory, str] = {
    ComplaintCategory.SANITATION: "SAN",
    ComplaintCategory.DRAINAGE: "DRN",
    ComplaintCategory.WATERLOGGING: "WTR",
    ComplaintCategory.ROADS: "ROAD",
    ComplaintCategory.STREET_LIGHTS: "LGT",
    ComplaintCategory.WATER_SUPPLY: "WSP",
    ComplaintCategory.TRAFFIC: "TRF",
    ComplaintCategory.PUBLIC_HEALTH: "HLTH",
    ComplaintCategory.OTHER: "OTH",
}

DEFAULT_DEPARTMENTS: dict[ComplaintCategory, ComplaintDepartment] = {
    ComplaintCategory.SANITATION: ComplaintDepartment.SANITATION,
    ComplaintCategory.DRAINAGE: ComplaintDepartment.DRAINAGE,
    ComplaintCategory.WATERLOGGING: ComplaintDepartment.DRAINAGE,
    ComplaintCategory.ROADS: ComplaintDepartment.ROADS,
    ComplaintCategory.STREET_LIGHTS: ComplaintDepartment.ELECTRICAL,
    ComplaintCategory.WATER_SUPPLY: ComplaintDepartment.WATER_SUPPLY,
    ComplaintCategory.TRAFFIC: ComplaintDepartment.TRAFFIC,
    ComplaintCategory.PUBLIC_HEALTH: ComplaintDepartment.PUBLIC_HEALTH,
    ComplaintCategory.OTHER: ComplaintDepartment.MANUAL_REVIEW,
}

KNOWN_LOCALITIES = [
    "Kondapur",
    "Madhapur",
    "Gachibowli",
    "Kukatpally",
    "Ameerpet",
    "Jubilee Hills",
    "Charminar",
    "Begumpet",
    "Secunderabad",
    "Hitech City",
    "Banjara Hills",
    "Mehdipatnam",
    "Tolichowki",
    "Miyapur",
    "Tarnaka",
]


def create_complaint(db: Session, payload: ComplaintCreate) -> Complaint:
    reference_id = generate_reference_id(db, payload.category)
    complaint = Complaint(
        reference_id=reference_id,
        original_text=payload.original_text.strip(),
        normalized_english_text=payload.normalized_english_text,
        original_language=payload.original_language,
        detected_language=payload.detected_language,
        category=payload.category,
        subcategory=payload.subcategory,
        department=payload.department or DEFAULT_DEPARTMENTS[payload.category],
        priority=payload.priority,
        status=ComplaintStatus.SUBMITTED,
        latitude=payload.latitude,
        longitude=payload.longitude,
        landmark=payload.landmark,
        locality=payload.locality or _infer_locality(payload.landmark) or _infer_locality(payload.original_text),
        ward_name=payload.ward_name,
        ward_number=payload.ward_number,
        photo_url=payload.photo_url,
        analysis_source=payload.analysis_source,
        requires_human_verification=payload.requires_human_verification,
        reasoning_summary=payload.reasoning_summary,
    )
    _set_location(complaint)
    try:
        created = complaint_repository.create_complaint(db, complaint)
        db.commit()
        db.refresh(created)
        _attempt_duplicate_detection(db, created)
        db.refresh(created)
        return created
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database failure while creating complaint") from exc


def get_complaint_by_reference(db: Session, reference_id: str) -> Complaint:
    complaint = complaint_repository.get_by_reference_id(db, reference_id)
    if complaint is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Complaint {reference_id} was not found.")
    return complaint


def list_complaints(
    db: Session,
    *,
    search: str | None,
    category: ComplaintCategory | None,
    priority,
    status_filter,
    locality: str | None,
    ward_number: int | None,
    language: str | None,
    duplicate_status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Complaint], int]:
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid pagination. Use page >= 1 and page_size between 1 and 100.")
    return complaint_repository.list_complaints(
        db,
        search=search,
        category=category,
        priority=priority,
        status=status_filter,
        locality=locality,
        ward_number=ward_number,
        language=language,
        duplicate_status=duplicate_status,
        page=page,
        page_size=page_size,
    )


def update_complaint(db: Session, reference_id: str, payload: ComplaintUpdate) -> Complaint:
    complaint = get_complaint_by_reference(db, reference_id)
    updates = payload.model_dump(exclude_unset=True, by_alias=False)
    try:
        updated = complaint_repository.update_complaint(db, complaint, updates)
        db.commit()
        db.refresh(updated)
        return updated
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database failure while updating complaint") from exc


def generate_reference_id(db: Session, category: ComplaintCategory) -> str:
    prefix = CATEGORY_PREFIXES[category]
    suffix = complaint_repository.next_reference_number(db, prefix)
    return f"HYD-{prefix}-{suffix:04d}"


def map_points(
    db: Session,
    *,
    category: ComplaintCategory | None = None,
    priority=None,
    status_filter=None,
    locality: str | None = None,
) -> list[Complaint]:
    return complaint_repository.get_map_points(
        db,
        category=category,
        priority=priority,
        status=status_filter,
        locality=locality,
    )


def analytics(db: Session) -> dict[str, object]:
    from app.services.geospatial_service import get_hotspots

    return {
        "openComplaints": complaint_repository.count_open_complaints(db),
        "highPriorityIssues": complaint_repository.count_high_priority_complaints(db),
        "resolvedToday": complaint_repository.count_resolved_today(db),
        "possibleDuplicates": complaint_repository.count_duplicate_suggestions(
            db,
            status_filter=_duplicate_status("PENDING_REVIEW"),
        ),
        "confirmedDuplicates": complaint_repository.count_duplicate_suggestions(
            db,
            status_filter=_duplicate_status("CONFIRMED_DUPLICATE"),
        ),
        "rejectedDuplicateSuggestions": complaint_repository.count_duplicate_suggestions(
            db,
            status_filter=_duplicate_status("REJECTED"),
        ),
        "pendingDuplicateReviews": complaint_repository.count_duplicate_suggestions(
            db,
            status_filter=_duplicate_status("PENDING_REVIEW"),
        ),
        "complaintsByCategory": complaint_repository.complaints_by_category(db),
        "complaintsByDate": complaint_repository.complaints_by_date(db),
        "complaintsByLocality": complaint_repository.count_by_locality(db),
        "complaintsByWard": complaint_repository.count_by_ward(db),
        "hotspots": get_hotspots(db),
    }


def to_response(complaint: Complaint) -> ComplaintResponse:
    return ComplaintResponse.model_validate(complaint)


def _set_location(complaint: Complaint) -> None:
    if complaint.latitude is not None and complaint.longitude is not None:
        complaint.location = func.ST_SetSRID(func.ST_MakePoint(complaint.longitude, complaint.latitude), 4326)
    else:
        complaint.location = None


def _infer_locality(text: str | None) -> str | None:
    if not text:
        return None
    lower = text.lower()
    for locality in KNOWN_LOCALITIES:
        if locality.lower() in lower:
            return locality
    return None


def _attempt_duplicate_detection(db: Session, complaint: Complaint) -> None:
    from app.config import get_settings
    from app.services.duplicate_detection_service import detect_duplicate_candidates, try_generate_and_store_embedding

    if not get_settings().enable_duplicate_detection:
        return
    try:
        try_generate_and_store_embedding(db, complaint)
        detect_duplicate_candidates(db, complaint.id)
    except Exception:
        db.rollback()


def _duplicate_status(value: str):
    from app.models.complaint import DuplicateSuggestionStatus

    return DuplicateSuggestionStatus(value)
