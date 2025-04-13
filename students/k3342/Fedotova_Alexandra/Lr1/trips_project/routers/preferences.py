from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from connection import get_session
from models.models import Preference

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("", response_model=List[Preference])
def get_preferences(db: Session = Depends(get_session)):
    return db.exec(select(Preference)).all()

@router.post("", response_model=Preference)
def create_preference(preference: Preference, db: Session = Depends(get_session)):
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference

@router.delete("/{preference_id}")
def delete_preference(preference_id: int, db: Session = Depends(get_session)):
    preference = db.get(Preference, preference_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(preference)
    db.commit()
    return {"message": "Preference deleted successfully"}
