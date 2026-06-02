from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.complaint import Complaint
from app.services.duplicate_detection_service import try_generate_and_store_embedding


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill missing complaint embeddings.")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        complaints = list(
            db.scalars(
                select(Complaint)
                .where(Complaint.embedding.is_(None))
                .order_by(Complaint.created_at.asc())
                .limit(args.batch_size)
            )
        )
        print(f"Found {len(complaints)} complaint(s) without embeddings.")
        if args.dry_run:
            for complaint in complaints:
                print(f"DRY RUN: {complaint.reference_id}")
            return
        success = 0
        for complaint in complaints:
            if try_generate_and_store_embedding(db, complaint):
                success += 1
                print(f"Embedded {complaint.reference_id}")
            else:
                print(f"Skipped {complaint.reference_id}: embedding unavailable")
        print(f"Backfill complete: {success}/{len(complaints)} embedded.")


if __name__ == "__main__":
    main()
