from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import ComplaintCategory, ComplaintPriority, ComplaintStatus, SupportedLanguage
from app.schemas.complaint import (
    AdminComplaintList,
    AdminMapPoint,
    AnalyticsResponse,
    ComplaintResponse,
    ComplaintUpdate,
    HotspotResponse,
    NearbyComplaintResponse,
)
from app.services.complaint_service import analytics, list_complaints, map_points, update_complaint
from app.services.geospatial_service import get_hotspots, get_nearby_complaints

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/complaints", response_model=AdminComplaintList)
def get_admin_complaints(
    search: str | None = None,
    category: ComplaintCategory | None = None,
    priority: ComplaintPriority | None = None,
    status: ComplaintStatus | None = Query(default=None, alias="status"),
    locality: str | None = None,
    ward_number: int | None = Query(default=None, alias="ward_number"),
    language: SupportedLanguage | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AdminComplaintList:
    items, total = list_complaints(
        db,
        search=search,
        category=category,
        priority=priority,
        status_filter=status,
        locality=locality,
        ward_number=ward_number,
        language=language.value if language else None,
        page=page,
        page_size=page_size,
    )
    return AdminComplaintList(items=items, total=total, page=page, pageSize=page_size)


@router.patch("/complaints/{reference_id}", response_model=ComplaintResponse)
def patch_admin_complaint(
    reference_id: str,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    return update_complaint(db, reference_id, payload)


@router.get("/analytics", response_model=AnalyticsResponse)
def get_admin_analytics(db: Session = Depends(get_db)) -> dict[str, object]:
    return analytics(db)


@router.get("/map-points", response_model=list[AdminMapPoint])
def get_admin_map_points(db: Session = Depends(get_db)) -> list[AdminMapPoint]:
    points = map_points(db)
    return [
        AdminMapPoint(
            referenceId=complaint.reference_id,
            category=complaint.category,
            priority=complaint.priority,
            status=complaint.status,
            latitude=complaint.latitude,
            longitude=complaint.longitude,
            landmark=complaint.landmark,
            locality=complaint.locality,
        )
        for complaint in points
        if complaint.latitude is not None and complaint.longitude is not None
    ]


@router.get("/nearby-complaints", response_model=list[NearbyComplaintResponse])
def get_admin_nearby_complaints(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_meters: int = Query(default=200, ge=1, le=10_000),
    category: ComplaintCategory | None = None,
    db: Session = Depends(get_db),
) -> list[NearbyComplaintResponse]:
    return get_nearby_complaints(
        db,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        category=category,
    )


@router.get("/hotspots", response_model=list[HotspotResponse])
def get_admin_hotspots(
    radius_meters: int = Query(default=300, ge=1, le=10_000),
    min_complaints: int = Query(default=3, ge=2, le=100),
    category: ComplaintCategory | None = None,
    db: Session = Depends(get_db),
) -> list[HotspotResponse]:
    return get_hotspots(db, radius_meters=radius_meters, min_complaints=min_complaints, category=category)
