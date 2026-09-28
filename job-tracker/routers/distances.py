from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Distance
from schemas import DistanceCreate, DistanceOut, DistanceUpdate


class BulkImportRequest(BaseModel):
    text: str  # raw tab-separated paste from Google Sheets


class BulkImportResult(BaseModel):
    added: int
    updated: int
    skipped: int
    errors: list[str]

router = APIRouter(prefix="/api/distances", tags=["distances"])


@router.get("", response_model=list[DistanceOut])
def list_distances(db: Session = Depends(get_db)):
    return db.query(Distance).order_by(Distance.city).all()


@router.post("", response_model=DistanceOut, status_code=201)
def create_distance(payload: DistanceCreate, db: Session = Depends(get_db)):
    existing = db.query(Distance).filter(Distance.city == payload.city).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"City '{payload.city}' already exists")
    dist = Distance(**payload.model_dump())
    db.add(dist)
    db.commit()
    db.refresh(dist)
    return dist


@router.put("/{dist_id}", response_model=DistanceOut)
def update_distance(dist_id: int, payload: DistanceUpdate, db: Session = Depends(get_db)):
    dist = db.get(Distance, dist_id)
    if not dist:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dist, field, value)
    db.commit()
    db.refresh(dist)
    return dist


@router.delete("/{dist_id}", status_code=204)
def delete_distance(dist_id: int, db: Session = Depends(get_db)):
    dist = db.get(Distance, dist_id)
    if not dist:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(dist)
    db.commit()


@router.post("/bulk", response_model=BulkImportResult)
def bulk_import(payload: BulkImportRequest, db: Session = Depends(get_db)):
    """
    Accept a tab-separated paste from Google Sheets.
    Expected columns (in either order, auto-detected): City | Miles
    Rows where city already exists are updated, not duplicated.
    """
    added = updated = skipped = 0
    errors: list[str] = []

    for line_num, raw_line in enumerate(payload.text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 2:
            # Try comma as fallback (CSV export)
            parts = [p.strip() for p in line.split(",")]

        if len(parts) < 2:
            errors.append(f"Row {line_num}: couldn't parse '{line}' — expected two columns")
            continue

        # Auto-detect which column is the city and which is the number
        city_part, miles_part = parts[0], parts[1]
        try:
            miles = float(miles_part.replace(",", ""))
        except ValueError:
            # Maybe columns are reversed
            try:
                miles = float(city_part.replace(",", ""))
                city_part, miles_part = miles_part, city_part
            except ValueError:
                errors.append(f"Row {line_num}: couldn't parse miles from '{raw_line}'")
                continue

        city = city_part.strip()
        if not city:
            skipped += 1
            continue

        existing = db.query(Distance).filter(Distance.city.ilike(city)).first()
        if existing:
            existing.round_trip_miles = miles
            updated += 1
        else:
            db.add(Distance(city=city, round_trip_miles=miles))
            added += 1

    db.commit()
    return BulkImportResult(added=added, updated=updated, skipped=skipped, errors=errors)


@router.get("/lookup/{city}", response_model=DistanceOut | None)
def lookup_city(city: str, db: Session = Depends(get_db)):
    """Case-insensitive lookup — called by the frontend when location changes."""
    dist = db.query(Distance).filter(Distance.city.ilike(city)).first()
    return dist
