from app.models.complaint import ComplaintCategory, ComplaintDepartment, ComplaintPriority
from app.schemas.analysis import ComplaintAnalysisRequest, ComplaintAnalysisResponse, LLMComplaintAnalysis
from app.services.locality_preservation_service import extract_locality_terms


def analyse_with_keyword_fallback(
    request: ComplaintAnalysisRequest,
    normalized_text: str,
    *,
    detected_language: str | None = None,
    original_language: str | None = None,
    translation_provider: str | None = None,
) -> ComplaintAnalysisResponse:
    original_text = request.text.strip()
    text = normalized_text.strip() or original_text
    lower = f"{text} {original_text}".lower()
    location_text = _extract_location(text, original_text, request.landmark)
    category, subcategory, department, priority = _classify(lower)
    missing_fields = _missing_fields(request, location_text)
    follow_up = "Please share the exact location or select it on the map." if missing_fields else None
    issue_title = _title(subcategory)
    citizen_reply = _citizen_reply(category, location_text, follow_up)
    admin_summary = _admin_summary(issue_title, location_text)

    return ComplaintAnalysisResponse(
        originalText=original_text,
        normalizedEnglishText=text,
        originalLanguage=original_language,
        detectedLanguage=detected_language,
        category=category,
        subcategory=subcategory,
        department=department,
        priority=priority,
        locationText=location_text,
        missingFields=missing_fields,
        followUpQuestion=follow_up,
        citizenReply=citizen_reply,
        adminSummary=admin_summary,
        reasoningSummary=f"{issue_title} reported{f' near {location_text}' if location_text else ''}.",
        requiresHumanVerification=True,
        analysisSource="FALLBACK_RULES",
        translationProvider=translation_provider,
        issueTitle=issue_title,
        guardrailsApplied=[],
    )


def _classify(text: str) -> tuple[ComplaintCategory, str, ComplaintDepartment, ComplaintPriority]:
    if _has(text, ["live wire", "exposed electric wire", "sparking pole", "wire fallen", "electric pole fallen"]):
        return ComplaintCategory.STREET_LIGHTS, "ELECTRICAL_HAZARD", ComplaintDepartment.ELECTRICAL, ComplaintPriority.EMERGENCY
    if _has(text, ["fire", "smoke from transformer", "immediate danger"]):
        return ComplaintCategory.PUBLIC_HEALTH, "IMMEDIATE_DANGER", ComplaintDepartment.PUBLIC_HEALTH, ComplaintPriority.EMERGENCY
    if _has(text, ["sewage mixed with drinking water", "contaminated water", "foul-smelling drinking water"]):
        return ComplaintCategory.WATER_SUPPLY, "CONTAMINATED_WATER", ComplaintDepartment.WATER_SUPPLY, ComplaintPriority.HIGH
    if _has(text, ["garbage blocking drain", "waste clogging nala", "garbage causing waterlogging"]) or (
        _has(text, ["garbage", "trash", "waste", "dump", "kachra", "చెత్త", "کچرا"]) and _has(text, ["drain", "nala", "drainage"])
    ):
        return ComplaintCategory.SANITATION, "GARBAGE_BLOCKING_DRAIN", ComplaintDepartment.MULTI_DEPARTMENT, ComplaintPriority.HIGH
    if _has(text, ["water entering homes", "road fully blocked", "severe waterlogging", "vehicles unable to pass"]):
        return ComplaintCategory.WATERLOGGING, "SEVERE_WATERLOGGING", ComplaintDepartment.DRAINAGE, ComplaintPriority.HIGH
    if _has(text, ["waterlogging", "flood", "stagnant water", "standing water", "paani jama", "నీరు నిలిచింది", "road meeda water"]):
        return ComplaintCategory.WATERLOGGING, "ROAD_WATERLOGGING", ComplaintDepartment.DRAINAGE, ComplaintPriority.MEDIUM
    if _has(text, ["drain block ayindi", "blocked drain", "drain", "nala", "drainage", "కాలువ"]):
        return ComplaintCategory.DRAINAGE, "BLOCKED_DRAIN", ComplaintDepartment.DRAINAGE, ComplaintPriority.MEDIUM
    if _has(text, ["garbage", "trash", "waste", "dump", "kachra", "చెత్త", "کچرا"]):
        return ComplaintCategory.SANITATION, "GARBAGE_ACCUMULATION", ComplaintDepartment.SANITATION, ComplaintPriority.MEDIUM
    if _has(text, ["open manhole", "uncovered drain hole", "deep open drain"]):
        return ComplaintCategory.ROADS, "OPEN_MANHOLE", ComplaintDepartment.ROADS, ComplaintPriority.HIGH
    if _has(text, ["pothole", "damaged road", "broken road", "gadda", "గుంత"]):
        return ComplaintCategory.ROADS, "POTHOLE", ComplaintDepartment.ROADS, ComplaintPriority.HIGH
    if _has(text, ["street light", "light not working", "dark road", "వీధి దీపం"]):
        return ComplaintCategory.STREET_LIGHTS, "BROKEN_STREET_LIGHT", ComplaintDepartment.ELECTRICAL, ComplaintPriority.LOW
    if _has(text, ["no water", "pipeline leak", "water supply", "paani nahi aa raha", "నీళ్లు రావడం లేదు"]):
        return ComplaintCategory.WATER_SUPPLY, "WATER_SUPPLY_ISSUE", ComplaintDepartment.WATER_SUPPLY, ComplaintPriority.MEDIUM
    if _has(text, ["signal not working", "traffic light", "traffic jam", "traffic signal", "ట్రాఫిక్"]):
        return ComplaintCategory.TRAFFIC, "TRAFFIC_SIGNAL_ISSUE", ComplaintDepartment.TRAFFIC, ComplaintPriority.HIGH
    if _has(text, ["mosquito", "fever", "public health"]):
        return ComplaintCategory.PUBLIC_HEALTH, "PUBLIC_HEALTH_CONCERN", ComplaintDepartment.PUBLIC_HEALTH, ComplaintPriority.MEDIUM
    return ComplaintCategory.OTHER, "MISCELLANEOUS", ComplaintDepartment.MANUAL_REVIEW, ComplaintPriority.LOW


def build_fallback_model(request: ComplaintAnalysisRequest, normalized_text: str) -> LLMComplaintAnalysis:
    response = analyse_with_keyword_fallback(request, normalized_text)
    return LLMComplaintAnalysis(
        category=response.category,
        subcategory=response.subcategory,
        department=response.department,
        priority=response.priority,
        locationText=response.location_text,
        missingFields=response.missing_fields,
        followUpQuestion=response.follow_up_question,
        citizenReply=response.citizen_reply,
        adminSummary=response.admin_summary,
        reasoningSummary=response.reasoning_summary,
    )


def _extract_location(text: str, original_text: str, landmark: str | None) -> str | None:
    if landmark:
        return landmark
    for term in extract_locality_terms(f"{text} {original_text}"):
        return term
    lower = text.lower()
    if "near " in lower:
        return text[lower.index("near ") + 5 :].strip(" .")
    return None


def _missing_fields(request: ComplaintAnalysisRequest, location_text: str | None) -> list[str]:
    missing = []
    if request.latitude is None or request.longitude is None:
        missing.append("gps_location")
    if not location_text:
        missing.append("location")
    return missing


def _citizen_reply(category: ComplaintCategory, location_text: str | None, follow_up: str | None) -> str:
    issue = category.value.replace("_", " ").lower()
    if follow_up:
        return f"We identified a possible {issue} issue. {follow_up}"
    return f"We identified a possible {issue} issue{f' near {location_text}' if location_text else ''}. Field verification is required."


def _admin_summary(issue_title: str, location_text: str | None) -> str:
    return f"{issue_title} reported{f' near {location_text}' if location_text else ''}. Field verification is required."


def _title(subcategory: str) -> str:
    return subcategory.replace("_", " ").title()


def _has(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)
