from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagRead, TagUpdate
from app.crud.tag import get_tag, get_tags, create_tag, update_tag, delete_tag

router = APIRouter()

@router.get("/", response_model=list[TagRead])
def read_tags(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    tags = get_tags(session, skip, limit)
    return tags

@router.get("/{tag_id}", response_model=TagRead)
def read_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = get_tag(session, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.post("/", response_model=TagRead)
def create_new_tag(tag: TagCreate, session: Session = Depends(get_session)):
    db_tag = Tag(**tag.dict())
    created = create_tag(session, db_tag)
    return created

@router.put("/{tag_id}", response_model=TagRead)
def update_existing_tag(tag_id: int, tag_update: TagUpdate, session: Session = Depends(get_session)):
    db_tag = get_tag(session, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    update_data = tag_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)
    updated = update_tag(session, db_tag)
    return updated

@router.delete("/{tag_id}")
def delete_existing_tag(tag_id: int, session: Session = Depends(get_session)):
    db_tag = get_tag(session, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    delete_tag(session, db_tag)
    return {"detail": "Tag deleted"}
