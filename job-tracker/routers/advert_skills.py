from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AdvertSkill
from schemas import SkillCreate, AdvertSkillFrequency

router = APIRouter(prefix="/api/advert-skills", tags=["advert-skills"])


@router.get("/frequency", response_model=list[AdvertSkillFrequency])
def advert_skill_frequency(limit: int = 50, db: Session = Depends(get_db)):
    """Return advert skills ranked by how many times they've been logged."""
    rows = [s for (s,) in db.query(AdvertSkill.skill).all()]
    counts = Counter(s.lower() for s in rows)
    seen: dict[str, str] = {}
    for s in rows:
        if s.lower() not in seen:
            seen[s.lower()] = s
    return [
        AdvertSkillFrequency(skill=seen[k], count=v)
        for k, v in counts.most_common(limit)
    ]


@router.post("", response_model=AdvertSkillFrequency, status_code=201)
def add_advert_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    """Log one sighting of a skill seen in a job advert."""
    skill = AdvertSkill(skill=payload.skill.strip())
    db.add(skill)
    db.commit()
    # Return the updated count for this skill
    count = db.query(AdvertSkill).filter(
        AdvertSkill.skill.ilike(payload.skill.strip())
    ).count()
    return AdvertSkillFrequency(skill=payload.skill.strip(), count=count)


@router.delete("/decrement/{skill_name}", status_code=200)
def decrement_advert_skill(skill_name: str, db: Session = Depends(get_db)):
    """Remove one occurrence of a skill (decrement by 1)."""
    row = db.query(AdvertSkill).filter(
        AdvertSkill.skill.ilike(skill_name)
    ).order_by(AdvertSkill.created_at.desc()).first()
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(row)
    db.commit()
    count = db.query(AdvertSkill).filter(
        AdvertSkill.skill.ilike(skill_name)
    ).count()
    return {"skill": skill_name, "count": count}


@router.delete("/{skill_name}", status_code=204)
def delete_advert_skill(skill_name: str, db: Session = Depends(get_db)):
    """Remove all occurrences of a skill."""
    rows = db.query(AdvertSkill).filter(AdvertSkill.skill.ilike(skill_name)).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Skill not found")
    for row in rows:
        db.delete(row)
    db.commit()
