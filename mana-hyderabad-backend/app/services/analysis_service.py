from app.models.complaint import ComplaintCategory, ComplaintPriority
from app.schemas.complaint import ComplaintAnalysisRequest, ComplaintAnalysisResponse


LOCALITIES = [
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
]


def analyse_complaint(request: ComplaintAnalysisRequest) -> ComplaintAnalysisResponse:
    text = request.text.strip()
    lower = text.lower()
    category, subcategory, priority, issue = _classify(lower)
    location_text = _extract_location(text)
    missing_fields = []
    if request.latitude is None:
        missing_fields.append("latitude")
    if request.longitude is None:
        missing_fields.append("longitude")

    return ComplaintAnalysisResponse(
        normalizedEnglishText=_normalize_text(text, category, location_text, issue),
        category=category,
        subcategory=subcategory,
        priority=priority,
        locationText=location_text,
        missingFields=missing_fields,
        followUpQuestion=(
            "Please share the exact location or select it on the map."
            if missing_fields
            else None
        ),
    )


def _classify(text: str) -> tuple[ComplaintCategory, str, ComplaintPriority, str]:
    if _has(text, ["garbage", "trash", "waste", "dump", "చెత్త", "కచరా", "kooda", "kachra"]):
        return ComplaintCategory.SANITATION, "GARBAGE_ACCUMULATION", ComplaintPriority.MEDIUM, "garbage accumulation"
    if _has(text, ["drain", "nala", "blocked drain", "నాలా", "నాలి", "नाला", "نالہ"]):
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
    if "near " in lower:
        return text[text.lower().index("near ") + 5 :].strip(" .")
    return None


def _normalize_text(text: str, category: ComplaintCategory, location_text: str | None, issue: str) -> str:
    if location_text:
        return f"There is {issue} near {location_text}."
    if category == ComplaintCategory.OTHER:
        return text
    return f"There is {issue}."
