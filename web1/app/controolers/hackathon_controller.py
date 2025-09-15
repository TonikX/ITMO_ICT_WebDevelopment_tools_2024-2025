from fastapi import HTTPException
from sqlmodel import select, Session
from app.models import *
from app.auth import auth_handler

def get_all_hackathons(session: Session) -> list[Hackathon]:
    return session.exec(select(Hackathon)).all()

def get_hackathon_by_id(hackathon_id: int, session: Session) -> HackathonFull:
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return hackathon

def create_hackathon(hackathon_data: HackathonCreate, user_id: int, session: Session) -> HackathonFull:
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    hackathon = Hackathon.model_validate(hackathon_data)
    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon

def update_hackathon(hackathon_id: int, updates: HackathonUpdate, user_id: int, session: Session) -> HackathonFull:
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(hackathon, key, value)

    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon

def delete_hackathon(hackathon_id: int, user_id: int, session: Session):
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")

    session.delete(hackathon)
    session.commit()
    return {"ok": True}
