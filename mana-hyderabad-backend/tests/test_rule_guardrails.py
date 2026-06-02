from app.schemas.analysis import LLMComplaintAnalysis
from app.services.rule_guardrails import apply_guardrails


def base_analysis() -> LLMComplaintAnalysis:
    return LLMComplaintAnalysis(
        category="OTHER",
        subcategory="MISCELLANEOUS",
        department="MANUAL_REVIEW",
        priority="LOW",
        locationText=None,
        missingFields=[],
        followUpQuestion=None,
        citizenReply="We identified a possible civic issue.",
        adminSummary="Possible civic issue. Field verification is required.",
        reasoningSummary="Civic issue reported.",
    )


def test_live_wire_sets_electrical_emergency():
    guarded, rules = apply_guardrails(base_analysis(), "Live electric wire fallen on road near school")

    assert guarded.department == "ELECTRICAL"
    assert guarded.priority == "EMERGENCY"
    assert "ELECTRICAL_EMERGENCY" in rules


def test_open_manhole_raises_priority():
    guarded, rules = apply_guardrails(base_analysis(), "Open manhole on main road near Kukatpally Metro")

    assert guarded.priority == "EMERGENCY"
    assert "OPEN_MANHOLE_SENSITIVE_LOCATION" in rules


def test_contaminated_water_sets_water_supply_high():
    guarded, rules = apply_guardrails(base_analysis(), "Sewage water is mixing with drinking water near Kondapur")

    assert guarded.category == "WATER_SUPPLY"
    assert guarded.department == "WATER_SUPPLY"
    assert guarded.priority == "HIGH"
    assert "DRINKING_WATER_RISK" in rules
