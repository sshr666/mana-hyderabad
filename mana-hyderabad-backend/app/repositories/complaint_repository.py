import uuid
from datetime import date, timedelta, timezone
from typing import Any

from sqlalchemy import Integer, Select, and_, case, cast, func, or_, select, text
from sqlalchemy.orm import Session

from app.models.complaint import (
    Complaint,
    ComplaintCategory,
    ComplaintDuplicateSuggestion,
    ComplaintPriority,
    ComplaintStatus,
    DuplicateResolutionStatus,
    DuplicateSuggestionStatus,
)


OPEN_STATUSES = [
    ComplaintStatus.SUBMITTED,
    ComplaintStatus.UNDER_REVIEW,
    ComplaintStatus.ASSIGNED,
    ComplaintStatus.IN_PROGRESS,
]


def create_complaint(db: Session, complaint: Complaint) -> Complaint:
    db.add(complaint)
    db.flush()
    db.refresh(complaint)
    return complaint


def get_by_reference_id(db: Session, reference_id: str) -> Complaint | None:
    return db.scalar(select(Complaint).where(Complaint.reference_id == reference_id.upper()))


def list_complaints(
    db: Session,
    *,
    search: str | None = None,
    category: ComplaintCategory | None = None,
    priority: ComplaintPriority | None = None,
    status: ComplaintStatus | None = None,
    locality: str | None = None,
    ward_number: int | None = None,
    language: str | None = None,
    duplicate_status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Complaint], int]:
    stmt: Select[tuple[Complaint]] = select(Complaint)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Complaint.reference_id.ilike(like),
                Complaint.original_text.ilike(like),
                Complaint.normalized_english_text.ilike(like),
                Complaint.landmark.ilike(like),
                Complaint.locality.ilike(like),
            )
        )
    if category:
        stmt = stmt.where(Complaint.category == category)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
    if status:
        stmt = stmt.where(Complaint.status == status)
    if locality:
        stmt = stmt.where(Complaint.locality.ilike(f"%{locality}%"))
    if ward_number is not None:
        stmt = stmt.where(Complaint.ward_number == ward_number)
    if language:
        stmt = stmt.where(
            or_(Complaint.original_language == language, Complaint.detected_language == language)
        )
    if duplicate_status:
        if duplicate_status == "PENDING_REVIEW":
            stmt = stmt.where(
                Complaint.id.in_(
                    select(ComplaintDuplicateSuggestion.source_complaint_id).where(
                        ComplaintDuplicateSuggestion.status == DuplicateSuggestionStatus.PENDING_REVIEW
                    )
                )
            )
        elif duplicate_status == "CONFIRMED_DUPLICATE":
            stmt = stmt.where(Complaint.duplicate_resolution_status == DuplicateResolutionStatus.CONFIRMED_DUPLICATE)
        elif duplicate_status == "KEEP_SEPARATE":
            stmt = stmt.where(Complaint.duplicate_resolution_status == DuplicateResolutionStatus.KEEP_SEPARATE)
        elif duplicate_status == "NONE":
            stmt = stmt.where(
                Complaint.duplicate_resolution_status.is_(None),
                ~Complaint.id.in_(select(ComplaintDuplicateSuggestion.source_complaint_id)),
            )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Complaint.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(items), total


def get_by_id(db: Session, complaint_id: uuid.UUID) -> Complaint | None:
    return db.get(Complaint, complaint_id)


def update_complaint(db: Session, complaint: Complaint, updates: dict[str, Any]) -> Complaint:
    for field, value in updates.items():
        setattr(complaint, field, value)
    db.flush()
    db.refresh(complaint)
    return complaint


def update_embedding(
    db: Session,
    complaint: Complaint,
    *,
    embedding: list[float],
    source_text: str,
) -> Complaint:
    complaint.embedding = embedding
    complaint.embedding_source_text = source_text
    complaint.embedding_generated_at = func.now()
    db.flush()
    db.refresh(complaint)
    return complaint


def count_open_complaints(db: Session) -> int:
    return db.scalar(select(func.count()).where(Complaint.status.in_(OPEN_STATUSES))) or 0


def count_duplicate_suggestions(db: Session, status_filter: DuplicateSuggestionStatus | None = None) -> int:
    stmt = select(func.count()).select_from(ComplaintDuplicateSuggestion)
    if status_filter:
        stmt = stmt.where(ComplaintDuplicateSuggestion.status == status_filter)
    return db.scalar(stmt) or 0


def count_high_priority_complaints(db: Session) -> int:
    return db.scalar(
        select(func.count()).where(Complaint.priority.in_([ComplaintPriority.HIGH, ComplaintPriority.EMERGENCY]))
    ) or 0


def count_resolved_today(db: Session) -> int:
    return db.scalar(
        select(func.count()).where(
            Complaint.status == ComplaintStatus.RESOLVED,
            func.date(Complaint.updated_at) == date.today(),
        )
    ) or 0


def complaints_by_category(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        select(Complaint.category, func.count()).group_by(Complaint.category).order_by(Complaint.category)
    ).all()
    return [{"category": row[0], "count": row[1]} for row in rows]


def complaints_by_date(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        select(func.date(Complaint.created_at), func.count())
        .group_by(func.date(Complaint.created_at))
        .order_by(func.date(Complaint.created_at))
    ).all()
    return [{"date": row[0].isoformat(), "count": row[1]} for row in rows]


def get_map_points(
    db: Session,
    *,
    category: ComplaintCategory | None = None,
    priority: ComplaintPriority | None = None,
    status: ComplaintStatus | None = None,
    locality: str | None = None,
) -> list[Complaint]:
    stmt = (
        select(Complaint)
        .where(
            Complaint.latitude.is_not(None),
            Complaint.longitude.is_not(None),
            Complaint.location.is_not(None),
            Complaint.latitude.between(-90, 90),
            Complaint.longitude.between(-180, 180),
        )
        .order_by(Complaint.created_at.desc())
    )
    if category:
        stmt = stmt.where(Complaint.category == category)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
    if status:
        stmt = stmt.where(Complaint.status == status)
    if locality:
        stmt = stmt.where(Complaint.locality.ilike(f"%{locality}%"))
    return list(db.scalars(stmt).all())


def get_nearby_complaints(
    db: Session,
    *,
    latitude: float,
    longitude: float,
    radius_meters: int,
    category: ComplaintCategory | None = None,
) -> list[tuple[Complaint, float]]:
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    distance = func.ST_Distance(Complaint.location, cast(point, Complaint.location.type)).label("distance_meters")
    stmt = (
        select(Complaint, distance)
        .where(Complaint.location.is_not(None))
        .where(func.ST_DWithin(Complaint.location, cast(point, Complaint.location.type), radius_meters))
        .order_by(distance)
    )
    if category:
        stmt = stmt.where(Complaint.category == category)
    return [(row[0], float(row[1])) for row in db.execute(stmt).all()]


def get_duplicate_candidates(
    db: Session,
    *,
    source: Complaint,
    radius_meters: int,
    time_window_hours: int,
    max_candidates: int,
) -> list[tuple[Complaint, float, float]]:
    if source.location is None or source.created_at is None:
        return []
    start = source.created_at - timedelta(hours=time_window_hours)
    end = source.created_at + timedelta(hours=time_window_hours)
    distance = func.ST_Distance(Complaint.location, source.location).label("distance_meters")
    stmt = (
        select(
            Complaint,
            distance,
            func.abs(func.extract("epoch", Complaint.created_at - source.created_at) / 3600).label(
                "time_difference_hours"
            ),
        )
        .where(
            Complaint.id != source.id,
            Complaint.location.is_not(None),
            Complaint.category == source.category,
            Complaint.created_at >= start,
            Complaint.created_at <= end,
            Complaint.status != ComplaintStatus.RESOLVED,
            func.ST_DWithin(Complaint.location, source.location, radius_meters),
        )
        .order_by(distance.asc())
        .limit(max_candidates)
    )
    return [(row[0], float(row[1]), float(row[2])) for row in db.execute(stmt).all()]


def upsert_duplicate_suggestion(
    db: Session,
    suggestion: ComplaintDuplicateSuggestion,
) -> ComplaintDuplicateSuggestion:
    existing = db.scalar(
        select(ComplaintDuplicateSuggestion).where(
            ComplaintDuplicateSuggestion.source_complaint_id == suggestion.source_complaint_id,
            ComplaintDuplicateSuggestion.candidate_complaint_id == suggestion.candidate_complaint_id,
        )
    )
    if existing:
        if existing.status == DuplicateSuggestionStatus.PENDING_REVIEW:
            existing.distance_meters = suggestion.distance_meters
            existing.time_difference_hours = suggestion.time_difference_hours
            existing.semantic_similarity = suggestion.semantic_similarity
            existing.category_match = suggestion.category_match
            existing.duplicate_score = suggestion.duplicate_score
            existing.confidence_label = suggestion.confidence_label
        db.flush()
        db.refresh(existing)
        return existing
    db.add(suggestion)
    db.flush()
    db.refresh(suggestion)
    return suggestion


def get_duplicate_suggestions_for_reference(
    db: Session,
    reference_id: str,
) -> list[tuple[ComplaintDuplicateSuggestion, Complaint, Complaint]]:
    source = get_by_reference_id(db, reference_id)
    if source is None:
        return []
    stmt = (
        select(ComplaintDuplicateSuggestion, Complaint)
        .join(Complaint, Complaint.id == ComplaintDuplicateSuggestion.candidate_complaint_id)
        .where(ComplaintDuplicateSuggestion.source_complaint_id == source.id)
        .order_by(ComplaintDuplicateSuggestion.duplicate_score.desc(), ComplaintDuplicateSuggestion.created_at.desc())
    )
    return [(row[0], source, row[1]) for row in db.execute(stmt).all()]


def get_duplicate_suggestion(
    db: Session,
    suggestion_id: uuid.UUID,
) -> tuple[ComplaintDuplicateSuggestion, Complaint, Complaint] | None:
    source_alias = Complaint
    stmt = (
        select(ComplaintDuplicateSuggestion)
        .where(ComplaintDuplicateSuggestion.id == suggestion_id)
    )
    suggestion = db.scalar(stmt)
    if suggestion is None:
        return None
    source = db.get(source_alias, suggestion.source_complaint_id)
    candidate = db.get(Complaint, suggestion.candidate_complaint_id)
    if source is None or candidate is None:
        return None
    return suggestion, source, candidate


def recent_complaints_for_duplicate_recheck(
    db: Session,
    *,
    hours: int,
    limit: int,
) -> list[Complaint]:
    cutoff = func.now() - text(f"interval '{int(hours)} hours'")
    return list(
        db.scalars(
            select(Complaint)
            .where(Complaint.created_at >= cutoff)
            .order_by(Complaint.created_at.desc())
            .limit(limit)
        ).all()
    )


def get_hotspots(
    db: Session,
    *,
    radius_meters: int,
    min_complaints: int,
    category: ComplaintCategory | None = None,
) -> list[dict[str, Any]]:
    stmt = (
        select(
            func.coalesce(Complaint.locality, "Unknown").label("locality"),
            Complaint.category,
            func.count().label("complaint_count"),
            func.avg(Complaint.latitude).label("center_latitude"),
            func.avg(Complaint.longitude).label("center_longitude"),
            func.max(Complaint.created_at).label("latest_complaint_at"),
        )
        .where(Complaint.locality.is_not(None))
        .group_by(func.coalesce(Complaint.locality, "Unknown"), Complaint.category)
        .having(func.count() >= min_complaints)
        .order_by(text("complaint_count DESC"))
    )
    if category:
        stmt = stmt.where(Complaint.category == category)
    return [
        {
            "locality": row.locality,
            "category": row.category,
            "complaintCount": row.complaint_count,
            "centerLatitude": float(row.center_latitude) if row.center_latitude is not None else None,
            "centerLongitude": float(row.center_longitude) if row.center_longitude is not None else None,
            "radiusMeters": radius_meters,
            "latestComplaintAt": row.latest_complaint_at,
        }
        for row in db.execute(stmt).all()
    ]


def count_by_locality(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        select(func.coalesce(Complaint.locality, "Unknown"), func.count())
        .group_by(func.coalesce(Complaint.locality, "Unknown"))
        .order_by(func.count().desc())
    ).all()
    return [{"locality": row[0], "count": row[1]} for row in rows]


def count_by_ward(db: Session) -> list[dict[str, Any]]:
    # TODO: Join against ward-boundary GeoJSON polygons when official ward data is available.
    rows = db.execute(
        select(Complaint.ward_number, Complaint.ward_name, func.count())
        .group_by(Complaint.ward_number, Complaint.ward_name)
        .order_by(case((Complaint.ward_number.is_(None), 1), else_=0), Complaint.ward_number)
    ).all()
    return [{"wardNumber": row[0], "wardName": row[1], "count": row[2]} for row in rows]


def next_reference_number(db: Session, prefix: str) -> int:
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:prefix))"), {"prefix": prefix})
    pattern = f"HYD-{prefix}-%"
    max_suffix = db.scalar(
        select(func.max(cast(func.substring(Complaint.reference_id, r"\d+$"), Integer))).where(
            Complaint.reference_id.like(pattern)
        )
    )
    return int(max_suffix or 0) + 1
