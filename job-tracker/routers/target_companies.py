import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import TargetCompany
from schemas import TargetCompanyCreate, TargetCompanyOut, TargetCompanyUpdate

router = APIRouter(prefix="/api/target-companies", tags=["target-companies"])


@router.get("", response_model=list[TargetCompanyOut])
def list_target_companies(
    category: Optional[str] = Query(None),
    max_distance: Optional[float] = Query(None),
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc"),
    db: Session = Depends(get_db),
):
    q = db.query(TargetCompany)
    if category:
        q = q.filter(TargetCompany.category == category)
    if max_distance is not None:
        q = q.filter(
            (TargetCompany.distance_miles <= max_distance) | TargetCompany.distance_miles.is_(None)
        )
    col = getattr(TargetCompany, sort_by, TargetCompany.name)
    if sort_dir == "asc":
        q = q.order_by(col.asc().nullslast())
    else:
        q = q.order_by(col.desc().nullslast())
    return q.all()


@router.post("", response_model=TargetCompanyOut, status_code=201)
def create_target_company(payload: TargetCompanyCreate, db: Session = Depends(get_db)):
    company = TargetCompany(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    # Map flexible header names to model fields
    col_map = {
        "company name": "name", "company": "name", "name": "name",
        "location": "location",
        "distance (miles)": "distance_miles", "distance": "distance_miles", "miles": "distance_miles",
        "careers page url": "careers_url", "careers url": "careers_url", "url": "careers_url",
        "category": "category",
    }

    reader = csv.DictReader(io.StringIO(text))
    imported = skipped = 0

    for row in reader:
        mapped = {col_map[k.strip().lower()]: v.strip()
                  for k, v in row.items() if k.strip().lower() in col_map}
        name = mapped.get("name")
        if not name:
            skipped += 1
            continue
        try:
            distance = float(mapped["distance_miles"]) if mapped.get("distance_miles") else None
        except ValueError:
            distance = None
        db.add(TargetCompany(
            name=name,
            location=mapped.get("location") or None,
            distance_miles=distance,
            category=mapped.get("category") or None,
            careers_url=mapped.get("careers_url") or None,
        ))
        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped}


@router.get("/{company_id}", response_model=TargetCompanyOut)
def get_target_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(TargetCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Not found")
    return company


@router.put("/{company_id}", response_model=TargetCompanyOut)
def update_target_company(company_id: int, payload: TargetCompanyUpdate, db: Session = Depends(get_db)):
    company = db.get(TargetCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


@router.post("/{company_id}/mark-checked", response_model=TargetCompanyOut)
def mark_checked(company_id: int, db: Session = Depends(get_db)):
    company = db.get(TargetCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Not found")
    company.last_checked = date.today()
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_target_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(TargetCompany, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(company)
    db.commit()
