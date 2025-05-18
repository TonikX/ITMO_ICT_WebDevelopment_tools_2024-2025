from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import select

from ..db.connection import get_session
from ..models.profile import Profile, ProfileBase
from ..models.profileLibrary import ProfileLibrary

router = APIRouter()


# Получить список всех профилей
@router.get("/profiles", response_model=List[Profile])
def get_profiles(session=Depends(get_session)):
    return session.exec(select(Profile)).all()


# Создать новый профиль
@router.post("/profiles", response_model=Profile)
def create_profile(profile: ProfileBase, session=Depends(get_session)):
    new_profile = Profile.model_validate(profile)
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    # Создаём библиотеку, связанную с этим профилем
    library = ProfileLibrary(profile_id=new_profile.id)
    session.add(library)
    session.commit()
    session.refresh(library)

    return new_profile


# Получить профиль по ID
@router.get("/profiles/{profile_id}", response_model=Profile)
def get_profile(profile_id: int, session=Depends(get_session)):
    profile = session.exec(
        select(Profile)
        .where(Profile.id == profile_id)).first()

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# Обновить профиль по ID
@router.patch("/profiles/{profile_id}", response_model=Profile)
def update_profile(profile_id: int,
                   profile_data: ProfileBase,
                   session=Depends(get_session)):

    profile = session.get(Profile, profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data_dict = profile_data.model_dump(exclude_unset=True)

    for key, value in profile_data_dict.items():
        setattr(profile, key, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


# Удалить профиль по ID
@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int, session=Depends(get_session)):
    profile = session.get(Profile, profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    session.delete(profile)
    session.commit()
    return {"status": 200, "message": "Profile deleted"}
