from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import select
from models.models import Profile
from models.default_models import ProfileDefault
from models.public_models import ProfilePublic
from connection import get_session
from typing_extensions import TypedDict
from auth_endpoints import auth_checker

profile_router = APIRouter()

@profile_router.get("/profile_list", response_model=list[ProfilePublic])
@auth_checker
async def get_profile_list(session=Depends(get_session)):
    return session.exec(select(Profile)).all()

@profile_router.patch("/profile/{id}")
async def update_profile(id: int, profile: ProfileDefault, session=Depends(get_session)) -> TypedDict("Response", {"status": int, "updated": Profile}):
    db_profile = session.get(Profile, id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Not found")
    data = profile.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_profile, key, value)
    session.commit()
    session.refresh(db_profile)
    return {"status": 202, "updated": db_profile}
