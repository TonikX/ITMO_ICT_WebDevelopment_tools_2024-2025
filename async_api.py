from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Skill, SkillBase
from async_connection import get_async_session, init_async_db

app = FastAPI(title="Async API Example")

@app.on_event("startup")
async def startup():
    await init_async_db()

@app.get("/async/skills/", response_model=List[Skill])
async def get_skills(session: AsyncSession = Depends(get_async_session)):
    """Асинхронно получает список всех навыков"""
    result = await session.execute(select(Skill))
    skills = result.scalars().all()
    return skills

@app.get("/async/skills/{skill_id}", response_model=Skill)
async def get_skill(skill_id: int, session: AsyncSession = Depends(get_async_session)):
    """Асинхронно получает навык по ID"""
    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post("/async/skills/", response_model=Skill)
async def create_skill(skill: SkillBase, session: AsyncSession = Depends(get_async_session)):
    """Асинхронно создает новый навык"""
    db_skill = Skill(**skill.dict())
    session.add(db_skill)
    await session.commit()
    await session.refresh(db_skill)
    return db_skill

@app.put("/async/skills/{skill_id}", response_model=Skill)
async def update_skill(skill_id: int, skill_data: SkillBase, session: AsyncSession = Depends(get_async_session)):
    """Асинхронно обновляет навык"""
    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    db_skill = result.scalars().first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Обновляем поля
    for key, value in skill_data.dict(exclude_unset=True).items():
        setattr(db_skill, key, value)
    
    session.add(db_skill)
    await session.commit()
    await session.refresh(db_skill)
    return db_skill

@app.delete("/async/skills/{skill_id}")
async def delete_skill(skill_id: int, session: AsyncSession = Depends(get_async_session)):
    """Асинхронно удаляет навык"""
    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    db_skill = result.scalars().first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    await session.delete(db_skill)
    await session.commit()
    return {"message": f"Skill {skill_id} has been deleted"}