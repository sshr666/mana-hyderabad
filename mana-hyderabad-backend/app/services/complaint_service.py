from datetime import date

from fastapi import HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintCategory, ComplaintPriority, ComplaintStatus
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate


CATEGORY_PREFIXES: dict[ComplaintCategory, str] = {
    ComplaintCategory.SANITATION: "SAN",
    ComplaintCategory.DRAINAGE: "DRN",
    ComplaintCategory.WATERLOGGING: "WTR",
    ComplaintCategory.ROADS: "ROAD",
    ComplaintCategory.STREET_LIGHTS: "LGT",
    ComplaintCategory.WATER_SUPPLY: "WAT",
    ComplaintCategory.TRAFFIC: "TRF",
    ComplaintCategory.OTHER: "OTH",
}

DEPARTMENTS: dict[ComplaintCategory, str] = {
    ComplaintCategory.SANITATION: "Sanitation",
    ComplaintCategory.DRAINAGE: "Drainage",
    ComplaintCategory.WATERLOGGING: "Drainage",
    ComplaintCategory.ROADS: "Roads",
    ComplaintCategory.STREET_LIGHTS: "Electrical",
    ComplaintCategory.WATER_SUPPLY: "Water Supply",
    ComplaintCategory.TRAFFIC: "Traffic",
    ComplaintCategory.OTHER: "Citizen Services",
}


def create_complaint(db: Session, payload: ComplaintCreate) -> Complaint:
    complaint = Complaint(
        reference_id=_generate_reference_id(db, payload.category),
        original_text=payload.original_text,
        normalized_english_text=payload.normalized_english_text,
        original_language=payload.original_language,
        category=payload.category,
        subcategory=payload.subcategory,
        priority=payload.priority,
        status=ComplaintStatus.SUBMITTED,
        latitude=payload.latitude,
        longitude=payload.longitude,
        landmark=payload.landmark,
        photo_url=payload.photo_url,
        department=DEPARTMENTS[payload.category],
    )
    _set_location(complaint)
    try:
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database failure while creating complaint") from exc


def get_complaint_by_reference(db: Session, reference_id: str) -> Complaint:
    complaint = db.scalar(select(Complaint).where(Complaint.reference_id == reference_id.upper()))
    if complaint is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Complaint {reference_id} was not found")
    return complaint


def list_complaints(
    db: Session,
    *,
    search: str | None,
    category: ComplaintCategory | None,
    priority: ComplaintPriority | None,
    status_filter: ComplaintStatus | None,
    locality: str | None,
    language: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Complaint], int]:
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid pagination. Use page >= 1 and page_size between 1 and 100.")

    stmt: Select[tuple[Complaint]] = select(Complaint)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            Complaint.reference_id.ilike(like)
            | Complaint.original_text.ilike(like)
            | Complaint.normalized_english_text.ilike(like)
            | Complaint.landmark.ilike(like)
        )
    if category:
        stmt = stmt.where(Complaint.category == category)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)
    if locality:
        stmt = stmt.where(Complaint.landmark.ilike(f"%{locality}%"))
    if language:
        stmt = stmt.where(Complaint.original_language == language)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Complaint.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(items), total


def update_complaint(db: Session, reference_id: str, payload: ComplaintUpdate) -> Complaint:
    complaint = get_complaint_by_reference(db, reference_id)
    updates = payload.model_dump(exclude_unset=True, by_alias=False)
    if "assigned_team" not in updates and "assignedTeam" in updates:
        updates["assigned_team"] = updates.pop("assignedTeam")
    for field, value in updates.items():
        setattr(complaint, field, value)
    _set_location(complaint)
    try:
        db.commit()
        db.refresh(complaint)
        return complaint
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database failure while updating complaint") from exc


def analytics(db: Session) -> dict[str, object]:
    open_statuses = [ComplaintStatus.SUBMITTED, ComplaintStatus.UNDER_REVIEW, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS]
    open_count = db.scalar(select(func.count()).where(Complaint.status.in_(open_statuses))) or 0
    high_count = db.scalar(
        select(func.count()).where(Complaint.priority.in_([ComplaintPriority.HIGH, ComplaintPriority.EMERGENCY]))
    ) or 0
    resolved_today = db.scalar(
        select(func.count()).where(
            Complaint.status == ComplaintStatus.RESOLVED,
            func.date(Complaint.updated_at) == date.today(),
        )
    ) or 0
    by_category = db.execute(
        select(Complaint.category, func.count()).group_by(Complaint.category).order_by(Complaint.category)
    ).all()
    by_date = db.execute(
        select(func.date(Complaint.created_at), func.count()).group_by(func.date(Complaint.created_at)).order_by(func.date(Complaint.created_at))
    ).all()
    return {
        "openComplaints": open_count,
        "highPriorityIssues": high_count,
        "resolvedToday": resolved_today,
        "possibleDuplicates": 0,
        "complaintsByCategory": [{"category": row[0], "count": row[1]} for row in by_category],
        "complaintsByDate": [{"date": row[0].isoformat(), "count": row[1]} for row in by_date],
    }


def map_points(db: Session) -> list[Complaint]:
    return list(
        db.scalars(
            select(Complaint)
            .where(Complaint.latitude.is_not(None), Complaint.longitude.is_not(None))
            .order_by(Complaint.created_at.desc())
        ).all()
    )


def _generate_reference_id(db: Session, category: ComplaintCategory) -> str:
    prefix = CATEGORY_PREFIXES[category]
    count = db.scalar(select(func.count()).where(Complaint.category == category)) or 0
    return f"HYD-{prefix}-{count + 1:04d}"


def _set_location(complaint: Complaint) -> None:
    if complaint.latitude is not None and complaint.longitude is not None:
        complaint.location = WKTElement(f"POINT({complaint.longitude} {complaint.latitude})", srid=4326)
    else:
        complaint.location = None
