from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.time_entry_model import TimeEntry, TimeEntryCreate, TimeEntryRead, TimeEntryUpdate
from connection import SessionLocal
from models.user_model import User
from models.task_model import Task
from util.auth import get_current_user

router = APIRouter()

def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=TimeEntryRead)
def create_time_entries(
    time_entries: TimeEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, существует ли задача, для которой создается запись времени
    task = session.get(Task, time_entries.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    new_entry = TimeEntry(
        task_id=time_entries.task_id,
        user_id=current_user.id,
        duration=time_entries.duration,
        comment=time_entries.comment
    )
    session.add(new_entry)
    session.commit()
    session.refresh(new_entry)
    return new_entry

@router.get("/", response_model=list[TimeEntryRead])
def list_time_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    entries = session.exec(
        select(TimeEntry).where(TimeEntry.user_id == current_user.id)
    ).all()
    return entries

@router.put("/{entry_id}", response_model=TimeEntryRead)
def update_time_entries(
    entry_id: int,
    time_entries_update: TimeEntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    entry = session.get(TimeEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    # Пользователь может редактировать только свои записи
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    update_data = time_entries_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)
    
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

@router.delete("/{entry_id}")
def delete_time_entries(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    entry = session.get(TimeEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    session.delete(entry)
    session.commit()
    return {"ok": True}