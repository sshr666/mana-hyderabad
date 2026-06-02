from app.schemas.vision import DetectedObject


LABEL_TEXT = {
    "garbage_heap": "garbage accumulation",
    "blocked_drain": "a possible blocked drain",
    "stagnant_water": "possible stagnant water",
    "pothole": "a possible pothole",
}


ADMIN_LABEL_TEXT = {
    "garbage_heap": "Garbage heap",
    "blocked_drain": "Possible blocked drain",
    "stagnant_water": "Possible stagnant water",
    "pothole": "Possible pothole",
}


def build_citizen_message(objects: list[DetectedObject]) -> str:
    labels = unique_labels(objects)
    if not labels:
        return (
            "The image was uploaded successfully. No supported issue type was confidently detected. "
            "Field verification may still be required."
        )
    if labels == ["garbage_heap", "blocked_drain"]:
        return "The image appears to show garbage accumulation and a possible drain blockage. Field verification is required."
    if labels == ["blocked_drain", "stagnant_water"]:
        return "The image appears to show a possible blocked drain and stagnant water. Field verification is required."
    descriptions = [LABEL_TEXT[label] for label in labels]
    if len(descriptions) == 1:
        return f"The image appears to show {descriptions[0]}. Field verification is required."
    return f"The image appears to show {join_phrase(descriptions)}. Field verification is required."


def build_admin_summary(objects: list[DetectedObject]) -> str:
    if not objects:
        return (
            "AI-assisted image analysis did not confidently detect the supported issue types. "
            "Review the uploaded image and verify on site."
        )
    lines = [
        f"{ADMIN_LABEL_TEXT[item.label]}: {round(item.confidence * 100)}%"
        for item in sorted(objects, key=lambda item: item.confidence, reverse=True)
    ]
    return (
        "AI-assisted image analysis detected: "
        + "; ".join(lines)
        + ". Review the uploaded image and verify the issue on site."
    )


def unique_labels(objects: list[DetectedObject]) -> list[str]:
    seen: list[str] = []
    for item in sorted(objects, key=lambda item: item.confidence, reverse=True):
        if item.label not in seen:
            seen.append(item.label)
    return seen


def join_phrase(parts: list[str]) -> str:
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"
