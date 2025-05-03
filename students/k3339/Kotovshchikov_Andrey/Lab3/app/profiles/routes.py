from typing import Annotated
from fastapi import APIRouter, Depends, Query

from profiles.depends import get_profile_service
from profiles.dtos import CriteriaDTO, ProfileCreateDTO, ProfileDTO, ProfileUpdateDTO
from profiles.services import ProfileService
from users.depends import get_current_user
from users.models import User

router = APIRouter(prefix="/profiles")


@router.get("/")
async def search_profiles(
    service: Annotated[ProfileService, Depends(get_profile_service)],
    skills: list[str] = Query(default=[]),
    work_experience: int = Query(default=0, ge=0),
    interests: list[str] = Query(default=[]),
):
    dto = CriteriaDTO(
        skills=skills,
        work_experience=work_experience,
        interests=interests,
    )

    return await service.search_profiles(dto)


@router.get("/me", response_model=ProfileDTO)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    return await service.get_my_profile(me=current_user)


@router.post("/me", response_model=ProfileDTO)
async def create_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    dto: ProfileCreateDTO,
):
    return await service.create_profile(me=current_user, dto=dto)


@router.patch("/me", response_model=ProfileDTO)
async def update_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    dto: ProfileUpdateDTO,
):
    return await service.update_profile(me=current_user, dto=dto)


@router.get("/skills")
async def get_allowed_skills(
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    return {"skills": await service.get_allowed_skills()}


@router.post("/me/skills/{skill_id:int}", response_model=ProfileDTO)
async def add_profile_skill(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    skill_id: int,
):
    return await service.add_profile_skill(me=current_user, skill_id=skill_id)


@router.delete("/me/skills/{skill_id:int}", response_model=ProfileDTO)
async def remove_profile_skill(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    skill_id: int,
):
    return await service.remove_profile_skill(me=current_user, skill_id=skill_id)
