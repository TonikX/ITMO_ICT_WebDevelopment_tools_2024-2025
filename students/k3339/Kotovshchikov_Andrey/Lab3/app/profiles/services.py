from fastapi import HTTPException, status
from sqlalchemy import exists, or_, select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from profiles.dtos import (
    CriteriaDTO,
    ProfileCreateDTO,
    ProfileDTO,
    ProfileListDTO,
    ProfileUpdateDTO,
    SkillDTO,
)
from profiles.models import Profile, ProfileSkill, Skill
from users.dtos import UserDTO


class ProfileService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_my_profile(self, me: UserDTO) -> ProfileDTO:
        stmt = (
            select(Profile)
            .where(Profile.user_id == me.id)
            .options(
                selectinload(Profile.skills),
                joinedload(Profile.user),
            )
        )

        profile = (await self._session.execute(stmt)).scalar()
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        return ProfileDTO.model_validate(profile)

    async def create_profile(self, me: UserDTO, dto: ProfileCreateDTO) -> ProfileDTO:
        stmt = exists().where(Profile.user_id == me.id).select()
        is_exists = (await self._session.execute(stmt)).scalar()
        if is_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile has already been created",
            )

        new_profile = Profile(**dto.model_dump(), user_id=me.id)
        self._session.add(new_profile)
        await self._session.commit()
        await self._session.refresh(new_profile)

        return ProfileDTO.model_validate(new_profile)

    async def update_profile(self, me: UserDTO, dto: ProfileUpdateDTO) -> ProfileDTO:
        stmt = select(Profile).where(Profile.user_id == me.id)
        profile = (await self._session.execute(stmt)).scalar()
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        dict_dto = dto.model_dump(exclude_unset=True)
        for key, value in dict_dto.items():
            setattr(profile, key, value)

        self._session.add(profile)
        await self._session.commit()
        await self._session.refresh(profile)

        return ProfileDTO.model_validate(profile)

    async def search_profiles(self, dto: CriteriaDTO) -> ProfileListDTO:
        search_list = []
        if dto.work_experience:
            search_list.append(Profile.work_experience >= dto.work_experience)

        if dto.skills:
            search_list.append(
                select(ProfileSkill)
                .join(Skill, ProfileSkill.skill_id == Skill.id)
                .where(
                    Skill.name.in_(dto.skills),
                    ProfileSkill.profile_id == Profile.id,
                )
                .exists()
            )

        if dto.interests:
            search_list.append(
                or_(
                    *[
                        Profile.about_me.like(f"%{interest}%")
                        for interest in dto.interests
                    ]
                )
            )

        stmt = select(Profile).where(*search_list)
        profiles = (await self._session.execute(stmt)).scalars().all()
        return ProfileListDTO(
            total=len(profiles),
            profiles=[ProfileDTO.model_validate(profile) for profile in profiles],
        )

    async def get_allowed_skills(self) -> list[SkillDTO]:
        stmt = select(Skill)
        skills = (await self._session.execute(stmt)).scalars().all()
        return [SkillDTO.model_validate(skill) for skill in skills]

    async def add_profile_skill(self, me: UserDTO, skill_id: int) -> ProfileDTO:
        stmt = select(Profile).where(Profile.user_id == me.id)
        profile = (await self._session.execute(stmt)).scalar()
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        stmt = select(Skill).where(Skill.id == skill_id)
        skill = (await self._session.execute(stmt)).scalar()
        if skill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found",
            )

        if skill in profile.skills:
            return ProfileDTO.model_validate(profile)

        profile.skills.append(skill)
        self._session.add(profile)
        await self._session.commit()
        await self._session.refresh(profile)

        return ProfileDTO.model_validate(profile)

    async def remove_profile_skill(self, me: UserDTO, skill_id: int) -> ProfileDTO:
        stmt = select(Profile).where(Profile.user_id == me.id)
        profile = (await self._session.execute(stmt)).scalar()
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        stmt = select(Skill).where(Skill.id == skill_id)
        skill = (await self._session.execute(stmt)).scalar()
        if skill is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found",
            )

        if skill not in profile.skills:
            return ProfileDTO.model_validate(profile)

        profile.skills.remove(skill)
        self._session.add(profile)
        await self._session.commit()
        await self._session.refresh(profile)

        return ProfileDTO.model_validate(profile)
