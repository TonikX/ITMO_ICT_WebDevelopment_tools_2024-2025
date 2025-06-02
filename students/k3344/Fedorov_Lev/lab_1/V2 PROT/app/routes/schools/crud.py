from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from pydantic import BaseModel

from ..schemas.schools_schemas import SportSchoolResponse, SportSchoolCreate, SportSchoolUpdate
from ...models import SportSchool
from ...db import get_session

router = APIRouter(prefix="/schools", tags=["schools"])




@router.post("/", response_model=SportSchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(school: SportSchoolCreate, session: AsyncSession = Depends(get_session)):
    db_school = SportSchool(**school.dict())
    session.add(db_school)
    await session.commit()
    await session.refresh(db_school)
    return db_school


@router.get("/", response_model=List[SportSchoolResponse])
async def get_schools(
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        city: Optional[str] = None,
        session: AsyncSession = Depends(get_session)
):
    query = select(SportSchool)

    if name:
        query = query.filter(SportSchool.name.ilike(f"%{name}%"))
    if city:
        query = query.filter(SportSchool.city.ilike(f"%{city}%"))

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{school_id}", response_model=SportSchoolResponse)
async def get_school(school_id: int, session: AsyncSession = Depends(get_session)):
    query = select(SportSchool).where(SportSchool.school_id == school_id)
    result = await session.execute(query)
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Школы с айди {school_id} не существует"
        )

    return school


@router.put("/{school_id}", response_model=SportSchoolResponse)
async def update_school(
        school_id: int,
        school_data: SportSchoolUpdate,
        session: AsyncSession = Depends(get_session)
):
    query = select(SportSchool).where(SportSchool.school_id == school_id)
    result = await session.execute(query)
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Школы с айди {school_id} не существует"
        )

    update_data = school_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(school, key, value)

    await session.commit()
    await session.refresh(school)
    return school


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(school_id: int, session: AsyncSession = Depends(get_session)):
    query = select(SportSchool).where(SportSchool.school_id == school_id)
    result = await session.execute(query)
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Школы с айди {school_id} не существует"
        )

    await session.delete(school)
    await session.commit()
    return None
