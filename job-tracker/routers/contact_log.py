from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ContactLog, ReachOutType
from schemas import ContactLogCreate, ContactLogUpdate, ContactLogOut, ReachOutTypeOut

router = APIRouter(tags=["contact-log"])


# ── Reach out types ──────────────────────────────────────────────────────────

@router.get("/api/reach-out-types", response_model=list[ReachOutTypeOut])
def list_reach_out_types(db: Session = Depends(get_db)):
    return db.query(ReachOutType).order_by(ReachOutType.name).all()


@router.post("/api/reach-out-types", response_model=ReachOutTypeOut, status_code=201)
def add_reach_out_type(payload: dict, db: Session = Depends(get_db)):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="name required")
    existing = db.query(ReachOutType).filter(ReachOutType.name.ilike(name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already exists")
    rot = ReachOutType(name=name)
    db.add(rot)
    db.commit()
    db.refresh(rot)
    return rot


@router.delete("/api/reach-out-types/{rot_id}", status_code=204)
def delete_reach_out_type(rot_id: int, db: Session = Depends(get_db)):
    rot = db.get(ReachOutType, rot_id)
    if not rot:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(rot)
    db.commit()


# ── Contact log ───────────────────────────────────────────────────────────────

@router.get("/api/contact-log", response_model=list[ContactLogOut])
def list_contacts(db: Session = Depends(get_db)):
    return db.query(ContactLog).order_by(ContactLog.date.desc().nullslast(), ContactLog.id.desc()).all()


@router.get("/api/contact-log/{entry_id}", response_model=ContactLogOut)
def get_contact(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(ContactLog, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    return entry


@router.post("/api/contact-log", response_model=ContactLogOut, status_code=201)
def create_contact(payload: ContactLogCreate, db: Session = Depends(get_db)):
    entry = ContactLog(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.patch("/api/contact-log/{entry_id}", response_model=ContactLogOut)
def update_contact(entry_id: int, payload: ContactLogUpdate, db: Session = Depends(get_db)):
    entry = db.get(ContactLog, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/api/contact-log/{entry_id}", status_code=204)
def delete_contact(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(ContactLog, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(entry)
    db.commit()
