import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Application
from schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status: Optional[str] = Query(None),
    agency_or_direct: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    job_type: Optional[str] = Query(None),
    exclude_contract: bool = Query(False),
    sort_by: str = Query("date"),
    sort_dir: str = Query("desc"),
    db: Session = Depends(get_db),
):
    q = db.query(Application).options(joinedload(Application.interview_dates))

    if status:
        q = q.filter(Application.status == status)
    if agency_or_direct:
        q = q.filter(Application.agency_or_direct == agency_or_direct)
    if location:
        q = q.filter(Application.location.ilike(f"%{location}%"))
    if source:
        q = q.filter(Application.source.ilike(f"%{source}%"))
    if search:
        q = q.filter(
            or_(
                Application.company.ilike(f"%{search}%"),
                Application.position.ilike(f"%{search}%"),
                Application.agency_name.ilike(f"%{search}%"),
            )
        )
    if date_from:
        q = q.filter(Application.date >= date_from)
    if date_to:
        q = q.filter(Application.date <= date_to)
    if job_type:
        q = q.filter(Application.job_type == job_type)
    if exclude_contract:
        q = q.filter(or_(Application.job_type != "Contract", Application.job_type.is_(None)))

    col = getattr(Application, sort_by, Application.date)
    if sort_dir == "asc":
        q = q.order_by(col.asc().nullslast())
    else:
        q = q.order_by(col.desc().nullslast())

    return q.all()


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(**payload.model_dump())
    today = date.today()
    if app.last_update is None:
        app.last_update = today
    # Initialise next_stage_updated so the stale-check clock starts from creation
    app.next_stage_updated = today
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("/export/csv")
def export_csv(
    status: Optional[str] = Query(None),
    agency_or_direct: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    job_type: Optional[str] = Query(None),
    exclude_contract: bool = Query(False),
    sort_by: str = Query("date"),
    sort_dir: str = Query("desc"),
    db: Session = Depends(get_db),
):
    q = db.query(Application).options(joinedload(Application.interview_dates))

    if status:
        q = q.filter(Application.status == status)
    if agency_or_direct:
        q = q.filter(Application.agency_or_direct == agency_or_direct)
    if location:
        q = q.filter(Application.location.ilike(f"%{location}%"))
    if source:
        q = q.filter(Application.source.ilike(f"%{source}%"))
    if search:
        q = q.filter(
            or_(
                Application.company.ilike(f"%{search}%"),
                Application.position.ilike(f"%{search}%"),
                Application.agency_name.ilike(f"%{search}%"),
            )
        )
    if date_from:
        q = q.filter(Application.date >= date_from)
    if date_to:
        q = q.filter(Application.date <= date_to)
    if job_type:
        q = q.filter(Application.job_type == job_type)
    if exclude_contract:
        q = q.filter(or_(Application.job_type != "Contract", Application.job_type.is_(None)))

    col = getattr(Application, sort_by, Application.date)
    if sort_dir == "asc":
        q = q.order_by(col.asc().nullslast())
    else:
        q = q.order_by(col.desc().nullslast())

    apps = q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "date", "company", "agency_name", "agency_or_direct", "applied_or_contacted",
        "position", "job_type", "wage_max", "expected_wage", "day_rate", "contract_length",
        "location", "office_days", "round_trip_miles", "source", "status", "next_stage",
        "last_update", "notes", "job_url", "interview_dates",
    ])
    for a in apps:
        interview_dates = " | ".join(
            str(d.interview_date) for d in sorted(a.interview_dates, key=lambda d: d.interview_date)
        )
        writer.writerow([
            a.id, a.date, a.company, a.agency_name, a.agency_or_direct, a.applied_or_contacted,
            a.position, a.job_type, a.wage_max, a.expected_wage, a.day_rate, a.contract_length,
            a.location, a.office_days, a.round_trip_miles, a.source, a.status, a.next_stage,
            a.last_update, a.notes, a.job_url, interview_dates,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    return app


@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")

    updates = payload.model_dump(exclude_unset=True)

    # If next_stage is being changed, reset the stale-check clock
    if "next_stage" in updates and updates["next_stage"] != app.next_stage:
        updates["next_stage_updated"] = date.today()

    for field, value in updates.items():
        setattr(app, field, value)

    app.last_update = date.today()
    db.commit()
    db.refresh(app)
    return app


@router.post("/{app_id}/duplicate", response_model=ApplicationOut, status_code=201)
def duplicate_application(app_id: int, db: Session = Depends(get_db)):
    src = db.get(Application, app_id)
    if not src:
        raise HTTPException(status_code=404, detail="Not found")
    today = date.today()
    copy = Application(
        date=today,
        company=src.company,
        agency_name=src.agency_name,
        agency_or_direct=src.agency_or_direct,
        applied_or_contacted=src.applied_or_contacted,
        position=src.position,
        job_type=src.job_type,
        wage_max=src.wage_max,
        expected_wage=src.expected_wage,
        day_rate=src.day_rate,
        contract_length=src.contract_length,
        location=src.location,
        office_days=src.office_days,
        round_trip_miles=src.round_trip_miles,
        source=src.source,
        last_update=today,
        next_stage_updated=today,
        notes=src.notes,
        job_url=src.job_url,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(app)
    db.commit()
