from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import anyio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.complaint import Complaint, VisionStatus
from app.services.vision_analysis_service import analyse_complaint_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill vision analysis for complaints with images.")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        stmt = select(Complaint).where(Complaint.photo_url.is_not(None)).order_by(Complaint.created_at.asc())
        if not args.force:
            stmt = stmt.where(
                (Complaint.vision_status.is_(None))
                | (Complaint.vision_status.in_([VisionStatus.NOT_REQUESTED, VisionStatus.FAILED, VisionStatus.NOT_CONFIGURED]))
            )
        complaints = list(db.scalars(stmt.limit(args.batch_size)))
        print(f"Found {len(complaints)} complaint(s) for vision backfill.")
        for complaint in complaints:
            if args.dry_run:
                print(f"DRY RUN: {complaint.reference_id}")
                continue
            result = anyio.run(analyse_complaint_image, db, complaint.reference_id)
            print(f"{complaint.reference_id}: {result.vision_status}")


if __name__ == "__main__":
    main()
