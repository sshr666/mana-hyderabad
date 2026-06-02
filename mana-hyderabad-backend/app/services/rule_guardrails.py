from app.models.complaint import ComplaintCategory, ComplaintDepartment, ComplaintPriority
from app.schemas.analysis import LLMComplaintAnalysis


PRIORITY_ORDER = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "EMERGENCY": 3,
}


def apply_guardrails(analysis: LLMComplaintAnalysis, complaint_text: str) -> tuple[LLMComplaintAnalysis, list[str]]:
    lower = complaint_text.lower()
    updates: dict[str, object] = {}
    rules: list[str] = []

    if _has(lower, ["live wire", "exposed electric wire", "sparking pole", "electric pole fallen", "wire fallen on road"]):
        updates["department"] = ComplaintDepartment.ELECTRICAL
        updates["priority"] = _max_priority(analysis.priority, ComplaintPriority.EMERGENCY)
        updates["category"] = ComplaintCategory.STREET_LIGHTS
        rules.append("ELECTRICAL_EMERGENCY")

    if _has(lower, ["fire", "smoke from transformer", "immediate danger"]):
        updates["priority"] = _max_priority(updates.get("priority", analysis.priority), ComplaintPriority.EMERGENCY)
        rules.append("IMMEDIATE_DANGER")

    if _has(lower, ["open manhole", "uncovered drain hole", "deep open drain"]):
        updates["priority"] = _max_priority(updates.get("priority", analysis.priority), ComplaintPriority.HIGH)
        if _has(lower, ["school", "hospital", "busy road", "main road"]):
            updates["priority"] = _max_priority(updates["priority"], ComplaintPriority.EMERGENCY)
            rules.append("OPEN_MANHOLE_SENSITIVE_LOCATION")
        else:
            rules.append("OPEN_MANHOLE_HIGH_PRIORITY")

    if _has(lower, ["water entering homes", "road fully blocked by flooding", "severe waterlogging", "vehicles unable to pass"]):
        updates["category"] = ComplaintCategory.WATERLOGGING
        updates["department"] = ComplaintDepartment.DRAINAGE
        updates["priority"] = _max_priority(updates.get("priority", analysis.priority), ComplaintPriority.HIGH)
        rules.append("SEVERE_FLOODING")

    if _has(
        lower,
        [
            "contaminated water",
            "sewage mixed with drinking water",
            "sewage water is mixing with drinking water",
            "foul-smelling drinking water",
        ],
    ):
        updates["category"] = ComplaintCategory.WATER_SUPPLY
        updates["department"] = ComplaintDepartment.WATER_SUPPLY
        updates["priority"] = _max_priority(updates.get("priority", analysis.priority), ComplaintPriority.HIGH)
        rules.append("DRINKING_WATER_RISK")

    if _has(lower, ["garbage blocking drain", "waste clogging nala", "garbage causing waterlogging"]) or (
        _has(lower, ["garbage", "trash", "waste"]) and _has(lower, ["drain", "nala"])
    ):
        updates["department"] = ComplaintDepartment.MULTI_DEPARTMENT
        updates["priority"] = _max_priority(updates.get("priority", analysis.priority), ComplaintPriority.HIGH)
        if not str(analysis.subcategory).startswith("GARBAGE_BLOCKING"):
            updates["subcategory"] = "GARBAGE_BLOCKING_DRAIN"
        rules.append("GARBAGE_DRAIN_OBSTRUCTION")

    if not rules:
        return analysis, []
    return analysis.model_copy(update=updates), rules


def _has(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _max_priority(current: object, proposed: ComplaintPriority) -> ComplaintPriority:
    current_value = getattr(current, "value", str(current))
    if PRIORITY_ORDER.get(current_value, 0) >= PRIORITY_ORDER[proposed.value]:
        return ComplaintPriority(current_value)
    return proposed
