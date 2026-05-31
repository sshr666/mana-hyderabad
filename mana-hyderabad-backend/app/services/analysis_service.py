from app.models.complaint import AnalysisSource, ComplaintCategory, ComplaintDepartment, ComplaintPriority
from app.schemas.complaint import ComplaintAnalysisRequest, ComplaintAnalysisResponse
from app.services.translation_service import normalize_complaint_to_english, translate_citizen_reply


LOCALITIES = [
    "Madhapur Metro",
    "Gachibowli signal",
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


async def analyse_complaint(request: ComplaintAnalysisRequest) -> ComplaintAnalysisResponse:
    original_text = request.text.strip()
    normalized = await normalize_complaint_to_english(original_text, request.language.value)
    text = normalized.normalized_english_text
    lower = text.lower()
    category, subcategory, priority, issue = _classify(lower)
    location_text = _extract_location(text)
    if not location_text:
        location_text = _extract_location(original_text)
    if request.landmark and not location_text:
        location_text = request.landmark
    missing_fields = []
    if request.latitude is None:
        missing_fields.append("latitude")
    if request.longitude is None:
        missing_fields.append("longitude")
    follow_up = "Please share the exact location or select it on the map." if missing_fields else None
    citizen_reply = None
    if follow_up:
        citizen_reply = (await translate_citizen_reply(follow_up, request.language.value)).translated_text

    return ComplaintAnalysisResponse(
        originalText=original_text,
        normalizedEnglishText=_normalize_text(text, category, location_text, issue),
        originalLanguage=request.language,
        detectedLanguage=normalized.detected_language,
        category=category,
        subcategory=subcategory,
        department=_department_for_category(category),
        priority=priority,
        locationText=location_text,
        missingFields=missing_fields,
        followUpQuestion=follow_up,
        citizenReply=citizen_reply,
        reasoningSummary=f"{issue.title()} reported{f' near {location_text}' if location_text else ''}.",
        requiresHumanVerification=True,
        analysisSource=AnalysisSource.FALLBACK_RULES,
        translationProvider=normalized.provider,
        issueTitle=subcategory.replace("_", " ").title(),
    )


def _classify(text: str) -> tuple[ComplaintCategory, str, ComplaintPriority, str]:
    if _has(text, ["garbage", "trash", "waste", "dump", "చెత్త", "కచరా", "kooda", "kachra", "کچرا", "كچرا"]):
        return ComplaintCategory.SANITATION, "GARBAGE_ACCUMULATION", ComplaintPriority.MEDIUM, "garbage accumulation"
    if _has(text, ["drain", "nala", "blocked drain", "నాలా", "నాలి", "नाला", "نالہ", "نالی"]):
        return ComplaintCategory.DRAINAGE, "BLOCKED_DRAIN", ComplaintPriority.MEDIUM, "blocked drain"
    if _has(text, ["waterlogging", "flood", "stagnant water", "standing water", "जलभराव"]):
        return ComplaintCategory.WATERLOGGING, "ROAD_WATERLOGGING", ComplaintPriority.MEDIUM, "waterlogging"
    if _has(text, ["pothole", "broken road", "road damage", "గుంత", "गड्ढा"]):
        return ComplaintCategory.ROADS, "POTHOLE", ComplaintPriority.HIGH, "road damage"
    if _has(text, ["street light", "streetlight", "dark road", "light not working", "వీధి దీపం"]):
        return ComplaintCategory.STREET_LIGHTS, "BROKEN_STREET_LIGHT", ComplaintPriority.LOW, "street light issue"
    if _has(text, ["water supply", "no water", "pipeline leak", "low pressure", "నీటి సరఫరా"]):
        return ComplaintCategory.WATER_SUPPLY, "WATER_SUPPLY_ISSUE", ComplaintPriority.MEDIUM, "water-supply issue"
    if _has(text, ["traffic light", "traffic signal", "signal", "ట్రాఫిక్", "ट्रैफिक"]):
        return ComplaintCategory.TRAFFIC, "SIGNAL_NOT_WORKING", ComplaintPriority.HIGH, "traffic signal problem"
    if _has(text, ["mosquito", "public health", "fever", "stray dog", "street dog"]):
        return ComplaintCategory.PUBLIC_HEALTH, "PUBLIC_HEALTH_CONCERN", ComplaintPriority.MEDIUM, "public health concern"
    return ComplaintCategory.OTHER, "MISCELLANEOUS", ComplaintPriority.LOW, "civic issue"


def _has(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_location(text: str) -> str | None:
    lower = text.lower()
    for locality in LOCALITIES:
        if locality.lower() in lower:
            if locality == "Gachibowli" and "signal" in lower:
                return "Gachibowli signal"
            return locality
    if "چارمینار" in text:
        return "Charminar"
    if "మాధాపూర్" in text:
        return "Madhapur Metro" if "మెట్రో" in text else "Madhapur"
    if "गाचीबोवली" in text:
        return "Gachibowli signal" if "सिग्नल" in text else "Gachibowli"
    if "near " in lower:
        return text[text.lower().index("near ") + 5 :].strip(" .")
    return None


def _normalize_text(text: str, category: ComplaintCategory, location_text: str | None, issue: str) -> str:
    if location_text:
        return f"There is {issue} near {location_text}."
    if category == ComplaintCategory.OTHER:
        return text
    return f"There is {issue}."


def _department_for_category(category: ComplaintCategory) -> ComplaintDepartment:
    departments = {
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
    return departments[category]
