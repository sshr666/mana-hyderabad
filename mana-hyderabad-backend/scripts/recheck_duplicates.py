from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.repositories.complaint_repository import recent_complaints_for_duplicate_recheck
from app.services.duplicate_detection_service import detect_duplicate_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-run duplicate detection for recent complaints.")
    parser.add_argument("--hours", type=int, default=72)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        complaints = recent_complaints_for_duplicate_recheck(db, hours=args.hours, limit=args.batch_size)
        print(f"Found {len(complaints)} recent complaint(s).")
        for complaint in complaints:
            if args.dry_run:
                print(f"DRY RUN: would recheck {complaint.reference_id}")
                continue
            suggestions = detect_duplicate_candidates(db, complaint.id)
            print(f"{complaint.reference_id}: {len(suggestions)} suggestion(s)")


if __name__ == "__main__":
    main()
