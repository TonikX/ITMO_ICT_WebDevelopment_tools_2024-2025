from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import UserSkill
from model.schemas.user_skill import UserSkillRead, UserSkillCreate, UserSkillUpdate

user_skill_router = APIRouter()


@user_skill_router.post("/", response_model=UserSkillRead)
def add_user_skill(user_skill: UserSkillCreate, session: Session = Depends(get_session)):
    db_user_skill = UserSkill.model_validate(user_skill)
    session.add(db_user_skill)
    session.commit()
    session.refresh(db_user_skill)
    return db_user_skill


@user_skill_router.get("/", response_model=List[UserSkillRead])
def get_user_skills(session: Session = Depends(get_session)):
    return session.exec(select(UserSkill)).all()


@user_skill_router.get("/{user_id}", response_model=List[UserSkillRead])
def get_skills_by_user(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()



@user_skill_router.patch("/{user_id}/{skill_id}", response_model=UserSkillRead)
def update_user_skill(user_id: int, skill_id: int, update: UserSkillUpdate, session: Session = Depends(get_session)):
    user_skill = session.get(UserSkill, (user_id, skill_id))
    if not user_skill:
        raise HTTPException(status_code=404, detail="UserSkill not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_skill, key, value)
    session.commit()
    session.refresh(user_skill)
    return user_skill


@user_skill_router.delete("/{user_id}/{skill_id}", response_model=dict)
def delete_user_skill(user_id: int, skill_id: int, session: Session = Depends(get_session)):
    user_skill = session.get(UserSkill, (user_id, skill_id))
    if not user_skill:
        raise HTTPException(status_code=404, detail="UserSkill not found")
    session.delete(user_skill)
    session.commit()
    return {"ok": True}
