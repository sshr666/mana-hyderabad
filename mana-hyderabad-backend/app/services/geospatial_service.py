from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.complaint import ComplaintCategory
from app.repositories import complaint_repository
from app.schemas.complaint import HotspotResponse, NearbyComplaintResponse


def get_nearby_complaints(
    db: Session,
    *,
    latitude: float,
    longitude: float,
    radius_meters: int = 200,
    category: ComplaintCategory | None = None,
) -> list[NearbyComplaintResponse]:
    if radius_meters < 1 or radius_meters > 10_000:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "radius_meters must be between 1 and 10000.")
    try:
        rows = complaint_repository.get_nearby_complaints(
            db,
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            category=category,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "PostGIS radius query failed") from exc

    return [
        NearbyComplaintResponse(
            referenceId=complaint.reference_id,
            category=complaint.category,
            priority=complaint.priority,
            status=complaint.status,
            latitude=complaint.latitude,
            longitude=complaint.longitude,
            landmark=complaint.landmark,
            locality=complaint.locality,
            distanceMeters=round(distance, 2),
        )
        for complaint, distance in rows
        if complaint.latitude is not None and complaint.longitude is not None
    ]


def get_hotspots(
    db: Session,
    *,
    radius_meters: int = 300,
    min_complaints: int = 3,
    category: ComplaintCategory | None = None,
) -> list[HotspotResponse]:
    if radius_meters < 1 or radius_meters > 10_000:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "radius_meters must be between 1 and 10000.")
    if min_complaints < 2 or min_complaints > 100:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "min_complaints must be between 2 and 100.")
    try:
        rows = complaint_repository.get_hotspots(
            db,
            radius_meters=radius_meters,
            min_complaints=min_complaints,
            category=category,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Hotspot query failed") from exc
    return [HotspotResponse(**row) for row in rows]


def get_complaints_grouped_by_locality(db: Session) -> list[dict[str, object]]:
    return complaint_repository.count_by_locality(db)


def get_complaints_grouped_by_ward(db: Session) -> list[dict[str, object]]:
    # TODO: Replace supplied ward values with point-in-polygon lookup when GHMC ward boundary GeoJSON is added.
    return complaint_repository.count_by_ward(db)
