from sqlalchemy import select

from app.database import SessionLocal
from app.models.complaint import Complaint, ComplaintCategory, ComplaintPriority, ComplaintStatus, SupportedLanguage
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint


SEED_COMPLAINTS = [
    {
        "referenceId": "HYD-DRN-0034",
        "originalText": "Garbage has blocked the drain near Kondapur RTO office.",
        "normalizedEnglishText": "Garbage has blocked the drain near Kondapur RTO office.",
        "originalLanguage": "en",
        "category": "DRAINAGE",
        "subcategory": "BLOCKED_DRAIN",
        "priority": "MEDIUM",
        "latitude": 17.4697,
        "longitude": 78.3578,
        "landmark": "Near Kondapur RTO office",
        "photoUrl": None,
        "status": ComplaintStatus.UNDER_REVIEW,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-SAN-0142",
        "originalText": "Madhapur metro దగ్గర garbage dump అయింది",
        "normalizedEnglishText": "Garbage has accumulated near Madhapur Metro.",
        "originalLanguage": "te",
        "category": "SANITATION",
        "subcategory": "GARBAGE_ACCUMULATION",
        "priority": "MEDIUM",
        "latitude": 17.4474,
        "longitude": 78.3915,
        "landmark": "Near Madhapur Metro",
        "photoUrl": None,
        "status": ComplaintStatus.ASSIGNED,
        "assigned_team": "Ward 107 Sanitation Crew",
    },
    {
        "referenceId": "HYD-WTR-0207",
        "originalText": "Road pe bahut waterlogging hai near Gachibowli signal",
        "normalizedEnglishText": "There is waterlogging near Gachibowli signal.",
        "originalLanguage": "hi",
        "category": "WATERLOGGING",
        "subcategory": "ROAD_WATERLOGGING",
        "priority": "HIGH",
        "latitude": 17.4401,
        "longitude": 78.3489,
        "landmark": "Gachibowli signal",
        "photoUrl": None,
        "status": ComplaintStatus.IN_PROGRESS,
        "assigned_team": "Stormwater Response Team",
    },
    {
        "referenceId": "HYD-ROAD-0081",
        "originalText": "Large pothole on the service road near Cyber Towers, Hitech City.",
        "normalizedEnglishText": "There is a large pothole on the service road near Cyber Towers, Hitech City.",
        "originalLanguage": "en",
        "category": "ROADS",
        "subcategory": "POTHOLE",
        "priority": "HIGH",
        "latitude": 17.4505,
        "longitude": 78.3804,
        "landmark": "Cyber Towers, Hitech City",
        "photoUrl": None,
        "status": ComplaintStatus.ASSIGNED,
        "assigned_team": "Road Repair Unit 2",
    },
    {
        "referenceId": "HYD-LGT-0049",
        "originalText": "Street light not working near Ameerpet metro entrance.",
        "normalizedEnglishText": "A street light is not working near Ameerpet metro entrance.",
        "originalLanguage": "en",
        "category": "STREET_LIGHTS",
        "subcategory": "BROKEN_STREET_LIGHT",
        "priority": "LOW",
        "latitude": 17.4355,
        "longitude": 78.4482,
        "landmark": "Ameerpet metro entrance",
        "photoUrl": None,
        "status": ComplaintStatus.SUBMITTED,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-WAT-0063",
        "originalText": "Water pressure is very low in Jubilee Hills Road No. 36.",
        "normalizedEnglishText": "Water pressure is very low in Jubilee Hills Road No. 36.",
        "originalLanguage": "en",
        "category": "WATER_SUPPLY",
        "subcategory": "LOW_PRESSURE",
        "priority": "MEDIUM",
        "latitude": 17.4308,
        "longitude": 78.4098,
        "landmark": "Jubilee Hills Road No. 36",
        "photoUrl": None,
        "status": ComplaintStatus.ASSIGNED,
        "assigned_team": "Water Board Zone C",
    },
    {
        "referenceId": "HYD-SAN-0188",
        "originalText": "چارمینار کے قریب کچرا جمع ہے",
        "normalizedEnglishText": "Garbage has accumulated near Charminar.",
        "originalLanguage": "ur",
        "category": "SANITATION",
        "subcategory": "GARBAGE_ACCUMULATION",
        "priority": "MEDIUM",
        "latitude": 17.3616,
        "longitude": 78.4747,
        "landmark": "Near Charminar",
        "photoUrl": None,
        "status": ComplaintStatus.SUBMITTED,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-DRN-0037",
        "originalText": "Open drain cover missing beside Begumpet flyover.",
        "normalizedEnglishText": "A drain cover is missing beside Begumpet flyover.",
        "originalLanguage": "en",
        "category": "DRAINAGE",
        "subcategory": "OPEN_DRAIN",
        "priority": "EMERGENCY",
        "latitude": 17.4447,
        "longitude": 78.4665,
        "landmark": "Beside Begumpet flyover",
        "photoUrl": None,
        "status": ComplaintStatus.IN_PROGRESS,
        "assigned_team": "Emergency Drainage Crew",
    },
    {
        "referenceId": "HYD-TRF-0048",
        "originalText": "Traffic signal is not working near Secunderabad station.",
        "normalizedEnglishText": "The traffic signal is not working near Secunderabad station.",
        "originalLanguage": "en",
        "category": "TRAFFIC",
        "subcategory": "SIGNAL_NOT_WORKING",
        "priority": "HIGH",
        "latitude": 17.4344,
        "longitude": 78.5011,
        "landmark": "Near Secunderabad station",
        "photoUrl": None,
        "status": ComplaintStatus.UNDER_REVIEW,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-SAN-0191",
        "originalText": "Kukatpally metro దగ్గర garbage చాలా ఉంది",
        "normalizedEnglishText": "There is a lot of garbage near Kukatpally Metro.",
        "originalLanguage": "te",
        "category": "SANITATION",
        "subcategory": "GARBAGE_ACCUMULATION",
        "priority": "MEDIUM",
        "latitude": 17.4933,
        "longitude": 78.4013,
        "landmark": "Near Kukatpally Metro",
        "photoUrl": None,
        "status": ComplaintStatus.SUBMITTED,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-WAT-0072",
        "originalText": "Pipeline leak outside Botanical Garden gate.",
        "normalizedEnglishText": "There is a pipeline leak outside Botanical Garden gate.",
        "originalLanguage": "en",
        "category": "WATER_SUPPLY",
        "subcategory": "PIPELINE_LEAK",
        "priority": "HIGH",
        "latitude": 17.4568,
        "longitude": 78.3632,
        "landmark": "Outside Botanical Garden gate",
        "photoUrl": None,
        "status": ComplaintStatus.UNDER_REVIEW,
        "assigned_team": None,
    },
    {
        "referenceId": "HYD-ROAD-0094",
        "originalText": "Construction debris blocking lane near Madhapur police station.",
        "normalizedEnglishText": "Construction debris is blocking a lane near Madhapur police station.",
        "originalLanguage": "en",
        "category": "ROADS",
        "subcategory": "CONSTRUCTION_DEBRIS",
        "priority": "MEDIUM",
        "latitude": 17.4483,
        "longitude": 78.3896,
        "landmark": "Near Madhapur police station",
        "photoUrl": None,
        "status": ComplaintStatus.RESOLVED,
        "assigned_team": "Road Clearance Unit",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(Complaint.id).limit(1))
        if existing:
            print("Seed skipped: complaints already exist.")
            return
        for seed_item in SEED_COMPLAINTS:
            item = seed_item.copy()
            reference_id = item.pop("referenceId")
            status = item.pop("status")
            assigned_team = item.pop("assigned_team")
            complaint = create_complaint(db, ComplaintCreate(**item))
            complaint.reference_id = reference_id
            complaint.status = status
            complaint.assigned_team = assigned_team
            db.add(complaint)
        db.commit()
        print(f"Seeded {len(SEED_COMPLAINTS)} complaints.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
