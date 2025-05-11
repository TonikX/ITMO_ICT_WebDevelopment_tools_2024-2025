from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select
from models.models import Profile
from models.default_models import ProfileDefault
from connection import get_session
from helpers import upd_model, get_object_by_id
from models.public_models import ProfilePublic, ProfilePatch
from .auth_endpoints import auth_checker
from jwt_logic import bearer_scheme
from typing_extensions import TypedDict

profile_router = APIRouter()

@profile_router.get("/profile_list", response_model=list[ProfilePublic])
async def get_profile_list(session=Depends(get_session)):
    found = session.exec(select(Profile)).all()
    return found

@profile_router.get("/profile/{id}", response_model=ProfilePublic)
@auth_checker
async def get_profile(profile_id: int, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                      session=Depends(get_session)):
    return get_object_by_id(profile_id, Profile, session)


@profile_router.post("/profile")
@auth_checker
async def create_profile(profile: ProfileDefault, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                         session=Depends(get_session)) -> TypedDict('Response', {"status": int, "created": Profile}):
    profile = Profile.model_validate(profile)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return {"status": 201, "created": profile}


@profile_router.delete("/profile/{id}")
@auth_checker
async def delete_profile(profile_id: int, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                         session=Depends(get_session)) -> TypedDict('Response', {"status": int, "msg": str}):
    profile = get_object_by_id(profile_id, Profile, session)
    session.delete(profile)
    session.commit()
    return { "status": 204, "msg": "profile deleted" }


@profile_router.patch("/profile/{id}")
@auth_checker
async def update_profile(profile_id: int, upd_profile: ProfilePatch, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                         session=Depends(get_session)) -> TypedDict('Response', {"status": int, "updated": Profile}):
    profile = get_object_by_id(profile_id, Profile, session)
    upd_data = upd_profile.model_dump(exclude_unset=True)
    profile = upd_model(profile, upd_data, session)
    return {"status": 202, "updated": profile}
