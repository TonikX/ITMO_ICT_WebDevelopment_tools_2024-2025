from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from model.models.models import Skill, UserSkill
from model.schemas.skill import SkillRead, SkillCreate, SkillUpdate, UsersSkillReadDetail
from model.schemas.user_skill import UserSkillRead

skill_router = APIRouter()

@skill_router.post("/", response_model=SkillRead)
def create_skill(skill: SkillCreate, session: Session = Depends(get_session)):
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@skill_router.get("/", response_model=List[SkillRead])
def get_skills(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()


@skill_router.get("/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@skill_router.patch("/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: int, update: SkillUpdate, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(skill, key, value)
    session.commit()
    session.refresh(skill)
    return skill

@skill_router.get("/{skill_id}/users", response_model=List[UsersSkillReadDetail])
def get_users_by_skill(skill_id: int, session: Session = Depends(get_session)):
    return session.exec(select(UserSkill).where(UserSkill.skill_id == skill_id)).all()


@skill_router.delete("/{skill_id}", response_model=dict)
def delete_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}
