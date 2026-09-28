from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Application, InterviewDate
from schemas import InterviewDateCreate, InterviewDateOut

router = APIRouter(tags=["interview_dates"])


@router.get("/api/applications/{app_id}/interview-dates", response_model=list[InterviewDateOut])
def list_interview_dates(app_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    return app.interview_dates


@router.post("/api/applications/{app_id}/interview-dates", response_model=InterviewDateOut, status_code=201)
def add_interview_date(app_id: int, payload: InterviewDateCreate, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    entry = InterviewDate(application_id=app_id, interview_date=payload.interview_date)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/api/interview-dates/{entry_id}", status_code=204)
def delete_interview_date(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(InterviewDate, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(entry)
    db.commit()
