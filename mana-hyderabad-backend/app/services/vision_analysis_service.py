from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from PIL import Image
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models.complaint import Complaint, VisionStatus
from app.repositories import complaint_repository
from app.schemas.vision import (
    BoundingBox,
    ComplaintVisionAnalysisResponse,
    DetectedObject,
    VisionAnalysisResponse,
    VisionHealthResponse,
)
from app.services.image_fetch_service import ImageFetchError, fetch_image_bytes
from app.services.vision_summary_service import build_admin_summary, build_citizen_message


ALLOWED_LABELS = {"garbage_heap", "blocked_drain", "stagnant_water", "pothole"}
_MODEL: Any | None = None
_MODEL_LOCK = asyncio.Lock()
_MODEL_LOAD_FAILED = False


class VisionModelNotConfigured(RuntimeError):
    pass


class VisionInferenceError(RuntimeError):
    pass


async def analyse_image_bytes(image_bytes: bytes) -> VisionAnalysisResponse:
    settings = get_settings()
    if not settings.enable_vision_analysis:
        return not_configured_response()
    try:
        model = await get_model()
    except VisionModelNotConfigured:
        return not_configured_response()
    started = time.perf_counter()
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            source_image = image.convert("RGB")
        results = model.predict(
            source=source_image,
            conf=settings.vision_confidence_threshold,
            iou=settings.vision_iou_threshold,
            imgsz=settings.vision_image_size,
            max_det=settings.vision_max_detections,
            device=resolve_device(settings.vision_device),
            verbose=False,
        )
        objects = parse_yolo_results(results)
    except Exception as exc:
        raise VisionInferenceError("Vision model inference failed.") from exc
    duration_ms = int((time.perf_counter() - started) * 1000)
    return VisionAnalysisResponse(
        status=VisionStatus.COMPLETED,
        detectedObjects=objects,
        citizenMessage=build_citizen_message(objects),
        adminSummary=build_admin_summary(objects),
        modelVersion=settings.vision_model_version,
        processedAt=datetime.now(timezone.utc),
        requiresHumanVerification=True,
        inferenceDurationMs=duration_ms,
    )


async def analyse_photo_url(photo_url: str) -> VisionAnalysisResponse:
    try:
        image_bytes = await fetch_image_bytes(photo_url)
    except ImageFetchError as exc:
        return failure_response(exc.code)
    try:
        return await analyse_image_bytes(image_bytes)
    except VisionInferenceError:
        return failure_response("INFERENCE_FAILED")


async def analyse_complaint_image(db: Session, reference_id: str) -> ComplaintVisionAnalysisResponse:
    complaint = complaint_repository.get_by_reference_id(db, reference_id)
    if complaint is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Complaint {reference_id} was not found.")
    if not complaint.photo_url:
        return to_complaint_vision_response(complaint)
    complaint_repository.update_vision_result(db, complaint, {"vision_status": VisionStatus.PENDING})
    db.commit()
    response = await analyse_photo_url(complaint.photo_url)
    updates = response_to_complaint_updates(response)
    if response.status == VisionStatus.FAILED:
        updates["vision_error_code"] = "VISION_ANALYSIS_FAILED"
    complaint_repository.update_vision_result(db, complaint, updates)
    db.commit()
    db.refresh(complaint)
    return to_complaint_vision_response(complaint)


def run_complaint_vision_analysis(reference_id: str) -> None:
    import anyio

    with SessionLocal() as db:
        anyio.run(analyse_complaint_image, db, reference_id)


def get_stored_complaint_vision_analysis(db: Session, reference_id: str) -> ComplaintVisionAnalysisResponse:
    complaint = complaint_repository.get_by_reference_id(db, reference_id)
    if complaint is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Complaint {reference_id} was not found.")
    return to_complaint_vision_response(complaint)


async def get_model():
    global _MODEL, _MODEL_LOAD_FAILED
    if _MODEL is not None:
        return _MODEL
    async with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        settings = get_settings()
        model_path = Path(settings.vision_model_path)
        if not model_path.exists():
            _MODEL_LOAD_FAILED = True
            raise VisionModelNotConfigured("Vision model weights are not configured.")
        try:
            from ultralytics import YOLO

            _MODEL = YOLO(str(model_path))
            _MODEL_LOAD_FAILED = False
            return _MODEL
        except Exception as exc:
            _MODEL_LOAD_FAILED = True
            raise VisionModelNotConfigured("Vision model could not be loaded.") from exc


def parse_yolo_results(results: Any) -> list[DetectedObject]:
    settings = get_settings()
    parsed: list[DetectedObject] = []
    for result in results or []:
        names = getattr(result, "names", {}) or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue
        xyxy_values = getattr(boxes, "xyxy", [])
        confidence_values = getattr(boxes, "conf", [])
        class_values = getattr(boxes, "cls", [])
        for xyxy, confidence, class_id in zip(xyxy_values, confidence_values, class_values):
            confidence_float = float(confidence)
            if confidence_float < settings.vision_confidence_threshold:
                continue
            label = names.get(int(class_id), str(int(class_id)))
            if label not in ALLOWED_LABELS:
                continue
            box = xyxy.tolist() if hasattr(xyxy, "tolist") else list(xyxy)
            bounding_box = None
            if settings.vision_store_bounding_boxes and len(box) == 4:
                bounding_box = BoundingBox(xMin=float(box[0]), yMin=float(box[1]), xMax=float(box[2]), yMax=float(box[3]))
            parsed.append(DetectedObject(label=label, confidence=confidence_float, boundingBox=bounding_box))
    return sorted(parsed, key=lambda item: item.confidence, reverse=True)[: settings.vision_max_detections]


def response_to_complaint_updates(response: VisionAnalysisResponse) -> dict[str, Any]:
    return {
        "vision_status": response.status,
        "vision_detected_objects": [item.model_dump(by_alias=True) for item in response.detected_objects],
        "vision_citizen_message": response.citizen_message,
        "vision_admin_summary": response.admin_summary,
        "vision_model_version": response.model_version,
        "vision_processed_at": response.processed_at,
        "requires_vision_human_verification": True,
        "vision_inference_duration_ms": response.inference_duration_ms,
        "vision_error_code": None if response.status == VisionStatus.COMPLETED else "VISION_UNAVAILABLE",
    }


def to_complaint_vision_response(complaint: Complaint) -> ComplaintVisionAnalysisResponse:
    objects = [
        DetectedObject.model_validate(item)
        for item in (complaint.vision_detected_objects or [])
        if isinstance(item, dict)
    ]
    return ComplaintVisionAnalysisResponse(
        complaintReferenceId=complaint.reference_id,
        visionStatus=complaint.vision_status or VisionStatus.NOT_REQUESTED,
        detectedObjects=objects,
        citizenMessage=complaint.vision_citizen_message,
        adminSummary=complaint.vision_admin_summary,
        modelVersion=complaint.vision_model_version,
        processedAt=complaint.vision_processed_at,
        requiresHumanVerification=complaint.requires_vision_human_verification,
        inferenceDurationMs=complaint.vision_inference_duration_ms,
    )


def not_configured_response() -> VisionAnalysisResponse:
    return VisionAnalysisResponse(
        status=VisionStatus.NOT_CONFIGURED,
        detectedObjects=[],
        citizenMessage=(
            "Image uploaded successfully. Automated image analysis is currently unavailable. "
            "Field verification may still be required."
        ),
        adminSummary="Computer-vision model is not configured. Review the uploaded image manually.",
        modelVersion=get_settings().vision_model_version,
        processedAt=datetime.now(timezone.utc),
        requiresHumanVerification=True,
        inferenceDurationMs=None,
    )


def failure_response(error_code: str) -> VisionAnalysisResponse:
    return VisionAnalysisResponse(
        status=VisionStatus.FAILED,
        detectedObjects=[],
        citizenMessage=(
            "Image uploaded successfully. Automated image analysis could not be completed. "
            "Field verification may still be required."
        ),
        adminSummary=f"Automated image analysis could not be completed. Review manually. Error code: {error_code}.",
        modelVersion=get_settings().vision_model_version,
        processedAt=datetime.now(timezone.utc),
        requiresHumanVerification=True,
        inferenceDurationMs=None,
    )


def vision_health() -> VisionHealthResponse:
    settings = get_settings()
    model_configured = Path(settings.vision_model_path).exists()
    return VisionHealthResponse(
        status="ok",
        enabled=settings.enable_vision_analysis,
        modelConfigured=model_configured,
        modelLoaded=_MODEL is not None,
        modelVersion=settings.vision_model_version,
        device=resolve_device(settings.vision_device),
    )


def resolve_device(device: str) -> str:
    if device != "auto":
        return device
    return "cpu"
