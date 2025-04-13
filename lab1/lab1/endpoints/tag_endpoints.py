from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.connection import get_session
from models.models import Tag
from models.tag import TagCreate, TagRead

tag_router = APIRouter(prefix="/tags", tags=["Tags"])


@tag_router.post("/", response_model=TagRead)
def create_tag(tag: TagCreate, session: Session = Depends(get_session)):
    db_tag = Tag(name=tag.name)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@tag_router.get("/", response_model=list[TagRead])
def get_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag)).all()
