from sqlalchemy.orm import Session
from app.models.tag import Tag, TransactionTag
from app.schemas.tag import TagCreate, TransactionTagCreate, TagUpdate


def create_tag(db: Session, tag: TagCreate):
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise ValueError("Tag name already exists")

    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tag).offset(skip).limit(limit).all()

def get_tag(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.tag_id == tag_id).first()


def update_tag(db: Session, tag_id: int, tag_data: TagUpdate):
    db_tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not db_tag:
        return None

    if tag_data.name:
        existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing:
            raise ValueError("Tag name already exists")

    db_tag.name = tag_data.name
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int):
    db_tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not db_tag:
        return False

    db.delete(db_tag)
    db.commit()
    return True

def add_tag_to_transaction(db: Session, transaction_id: int, tag_id: int, context: str | None = None):
    db_link = TransactionTag(
        transaction_id=transaction_id,
        tag_id=tag_id,
        context=context
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def remove_tag_from_transaction(db: Session, transaction_id: int, tag_id: int):
    db_link = db.query(TransactionTag).filter(
        TransactionTag.transaction_id == transaction_id,
        TransactionTag.tag_id == tag_id
    ).first()

    if not db_link:
        return False

    db.delete(db_link)
    db.commit()
    return True