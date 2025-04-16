from sqlmodel import Session, select
from app.models.tag import Tag

def get_tag(session: Session, tag_id: int) -> Tag:
    statement = select(Tag).where(Tag.id == tag_id)
    return session.exec(statement).first()

def get_tags(session: Session, skip: int = 0, limit: int = 100):
    statement = select(Tag).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_tag(session: Session, tag: Tag) -> Tag:
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

def update_tag(session: Session, tag: Tag) -> Tag:
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

def delete_tag(session: Session, tag: Tag):
    session.delete(tag)
    session.commit()
