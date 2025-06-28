# app/api/profiles.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.profile import Profile
from app.models.profile_skill import ProfileSkill
from app.schemas.profile import ProfileCreate, ProfileOut
from app.models.skill import Skill

router = APIRouter(prefix="/profiles", tags=["Profiles"])

# GET все профили (с фильтрами)
@router.get("/", response_model=list[ProfileOut])
@router.get("/", response_model=list[ProfileOut])
def read_profiles(
    experience: str | None = None,
    interests: str | None = None,
    skill: str | None = None,  # Новый параметр для фильтрации по навыку
    session: Session = Depends(get_session)
):
    query = session.query(Profile)

    if experience:
        query = query.filter(Profile.experience.ilike(f"%{experience}%"))
    if interests:
        query = query.filter(Profile.interests.ilike(f"%{interests}%"))

    if skill:
        # Фильтруем профили через связь с Skill
        query = query.join(Profile.skills).join(Skill).filter(Skill.name.ilike(f"%{skill}%"))

    profiles = query.all()
    return profiles

# GET профиль по ID
@router.get("/{profile_id}", response_model=ProfileOut)
def read_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# POST создать профиль
@router.post("/", response_model=ProfileOut)
def create_profile(profile_data: ProfileCreate, session: Session = Depends(get_session)):
    db_profile = Profile(**profile_data.dict(exclude={"skills"}))
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)

    for skill in profile_data.skills:
        skill_link = ProfileSkill(
            profile_id=db_profile.id,
            skill_id=skill.skill_id,
            level=skill.level
        )
        session.add(skill_link)
    session.commit()

    return db_profile

# PUT обновить профиль
@router.put("/{profile_id}", response_model=ProfileOut)
def update_profile(
    profile_id: int,
    profile_data: ProfileCreate,
    session: Session = Depends(get_session)
):
    db_profile = session.get(Profile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Обновляем поля
    for key, value in profile_data.dict(exclude={"skills"}).items():
        setattr(db_profile, key, value)

    # Обновляем навыки
    session.query(ProfileSkill).filter(ProfileSkill.profile_id == profile_id).delete()
    for skill in profile_data.skills:
        session.add(ProfileSkill(
            profile_id=db_profile.id,
            skill_id=skill.skill_id,
            level=skill.level
        ))

    session.commit()
    session.refresh(db_profile)
    return db_profile

# DELETE удалить профиль
@router.delete("/{profile_id}")
def delete_profile(profile_id: int, session: Session = Depends(get_session)):
    db_profile = session.get(Profile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    session.delete(db_profile)
    session.commit()
    return {"message": "Profile deleted"}