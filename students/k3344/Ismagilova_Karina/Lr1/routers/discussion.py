from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from auth.auth import authenticate_request, get_current_user
from models.models import Discussion, DiscussionCreate, User, DiscussionUpdate
from db import get_session

router = APIRouter(prefix="/discussions", tags=["Discussions"], dependencies=[Depends(authenticate_request)])


@router.get("/", response_model=List[Discussion])
def get_all_discussions(session: Session = Depends(get_session)):
    return session.exec(select(Discussion)).all()


@router.get("/{discussion_id}", response_model=Discussion)
def get_discussion(discussion_id: int, session: Session = Depends(get_session)):
    discussion = session.get(Discussion, discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Такого обсуждения нет")
    return discussion


@router.post("/", response_model=Discussion)
def create_discussion(
    discussion_data: DiscussionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    sent_time = datetime.utcnow().replace(microsecond=0)
    discussion = Discussion(
        **discussion_data.dict(),
        user_id=current_user.user_id,
        sent_at=sent_time
    )
    session.add(discussion)
    session.commit()
    session.refresh(discussion)
    return discussion


@router.patch("/{discussion_id}", response_model=Discussion)
def update_discussion(
    discussion_id: int,
    discussion_update: DiscussionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_discussion = session.get(Discussion, discussion_id)
    if not db_discussion:
        raise HTTPException(status_code=404, detail="Такого обсуждения нет")
    if db_discussion.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Вы не можете редактировать чужие обсуждения")

    if discussion_update.sent_at is None:
        discussion_update.sent_at = datetime.utcnow()
    update_data = discussion_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_discussion, key, value)
    session.commit()
    session.refresh(db_discussion)
    return db_discussion


@router.delete("/{discussion_id}")
def delete_discussion(discussion_id: int, session: Session = Depends(get_session)):
    discussion = session.get(Discussion, discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Такого обсуждения нет")
    session.delete(discussion)
    session.commit()
    return {"message": "Обсуждение успешно удалено"}
