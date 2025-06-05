from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Tag, TagCreate, TagRead
from connection import get_session
from auth.auth import auth_service
from models import User

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagRead)
def create_tag(
        tag: TagCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    db_tag = Tag(**tag.dict(), user_id=current_user.id)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.get("/", response_model=List[TagRead])
def read_tags(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    tags = session.exec(
        select(Tag)
        .where(Tag.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return tags


@router.get("/{tag_id}", response_model=TagRead)
def read_tag(
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}")
def delete_tag(
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
    return {"message": "Tag deleted successfully"}