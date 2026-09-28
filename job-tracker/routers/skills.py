from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Application, InterviewSkill
from schemas import SkillCreate, SkillOut, SkillFrequency

router = APIRouter(tags=["skills"])


@router.get("/api/applications/{app_id}/skills", response_model=list[SkillOut])
def list_skills(app_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    return app.skills


@router.post("/api/applications/{app_id}/skills", response_model=SkillOut, status_code=201)
def add_skill(app_id: int, payload: SkillCreate, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    skill = InterviewSkill(application_id=app_id, skill=payload.skill.strip())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/api/skills/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(InterviewSkill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(skill)
    db.commit()


@router.get("/api/skills/frequency", response_model=list[SkillFrequency])
def skill_frequency(limit: int = 20, db: Session = Depends(get_db)):
    """Return skills ranked by how many times they appear across all applications."""
    rows = [s for (s,) in db.query(InterviewSkill.skill).all()]
    counts = Counter(s.lower() for s in rows)
    # Preserve original capitalisation (first seen wins)
    seen: dict[str, str] = {}
    for s in rows:
        if s.lower() not in seen:
            seen[s.lower()] = s
    return [
        SkillFrequency(skill=seen[k], count=v)
        for k, v in counts.most_common(limit)
    ]
