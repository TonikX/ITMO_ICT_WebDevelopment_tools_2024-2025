from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

import app.schemas as schemas
from app.models.models import Profile, Tag, BookInfo, Book, ShareRequest, BookTagLink
from app.core.jwt import (
    hash_password,
    verify_password,
    create_access_token,
)


def get_profile_by_email(db: Session, email: str) -> Optional[Profile]:
    return db.exec(select(Profile).where(Profile.email == email)).first()

def authenticate_profile(db: Session, email: str, password: str) -> Optional[Profile]:
    prof = get_profile_by_email(db, email)
    if not prof or not verify_password(password, prof.password):
        return None
    return prof

def create_access_token_for_user(profile: Profile) -> str:
    return create_access_token({"user_id": profile.id})

def create_profile(db: Session, reg: schemas.Register) -> Profile:
    prof = Profile(
        name=reg.name,
        email=reg.email,
        password=hash_password(reg.password),
        description=reg.description,
        register_date=datetime.utcnow().date(),
        birth_date=reg.birth_date
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

def change_password(db: Session, prof: Profile, old: str, new: str) -> None:
    if not verify_password(old, prof.password):
        raise ValueError("Incorrect current password")
    prof.password = hash_password(new)
    db.add(prof)
    db.commit()


def get_profiles(db: Session) -> List[Profile]:
    return db.exec(select(Profile)).all()

def get_profile(db: Session, prof_id: int) -> Optional[Profile]:
    return db.get(Profile, prof_id)

def update_profile(db: Session, prof_id: int, patch: schemas.ProfilePatch) -> Profile:
    prof = db.get(Profile, prof_id)
    for f, v in patch.dict(exclude_unset=True).items():
        setattr(prof, f, v)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def get_tags(db: Session) -> List[Tag]:
    return db.exec(select(Tag)).all()

def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    return db.get(Tag, tag_id)

def create_tag(db: Session, name: str) -> Tag:
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

def update_tag(db: Session, tag_id: int, upd: schemas.TagUpdate) -> Tag:
    tag = db.get(Tag, tag_id)
    for f, v in upd.dict(exclude_unset=True).items():
        setattr(tag, f, v)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

def delete_tag(db: Session, tag_id: int) -> None:
    tag = db.get(Tag, tag_id)
    db.delete(tag)
    db.commit()


def get_bookinfos(db: Session) -> List[BookInfo]:
    stmt = (
        select(BookInfo)
        .options(
            selectinload(BookInfo.tags),
        )
    )
    return db.exec(stmt).all()

def get_bookinfo(db: Session, info_id: int) -> Optional[BookInfo]:
    stmt = (
        select(BookInfo)
        .where(BookInfo.id == info_id)
        .options(
            selectinload(BookInfo.tags),
        )
    )
    return db.exec(stmt).one_or_none()

def create_bookinfo(db: Session, bi: schemas.BookInfoCreate) -> BookInfo:
    info = BookInfo(
        title=bi.title,
        author=bi.author,
        release_date=bi.release_date,
        publisher=bi.publisher,
        genre=bi.genre
    )
    db.add(info)
    db.commit()
    db.refresh(info)
    for tag_id in bi.tag_ids:
        db.add(BookTagLink(info_id=info.id, tag_id=tag_id))
    db.commit()
    db.refresh(info)
    return info

def update_bookinfo(db: Session, info_id: int, upd: schemas.BookInfoUpdate) -> BookInfo:
    info = db.get(BookInfo, info_id)
    data = upd.dict(exclude_unset=True)
    if "tag_ids" in data:
        info.tags.clear()
        db.commit()
        for tid in data.pop("tag_ids") or []:
            db.add(BookTagLink(info_id=info.id, tag_id=tid))
    for f, v in data.items():
        setattr(info, f, v)
    db.add(info)
    db.commit()
    db.refresh(info)
    return info

def delete_bookinfo(db: Session, info_id: int) -> None:
    info = db.get(BookInfo, info_id)
    db.delete(info)
    db.commit()


def get_books(db: Session, title=None, author=None, tag_id=None) -> List[Book]:
    stmt = select(Book).options(
        selectinload(Book.info).selectinload(BookInfo.tags),
        selectinload(Book.owner)
    )
    if title:
        stmt = stmt.where(Book.info.title.ilike(f"%{title}%"))
    if author:
        stmt = stmt.where(Book.info.author.ilike(f"%{author}%"))
    if tag_id:
        stmt = stmt.where(Book.info.tags.any(tag_id=tag_id))
    return db.exec(stmt).all()

def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.exec(
        select(Book)
        .where(Book.id == book_id)
        .options(
            selectinload(Book.info).selectinload(BookInfo.tags),
            selectinload(Book.owner)
        )
    ).one_or_none()

def create_book(db: Session, bc: schemas.BookCreate) -> Book:
    book = Book(
        owner_id=bc.owner_id,
        info_id=bc.info_id,
        print_date=bc.print_date,
        own_since=bc.own_since
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def update_book(db: Session, book_id: int, upd: schemas.BookUpdate) -> Book:
    book = db.get(Book, book_id)
    for f, v in upd.dict(exclude_unset=True).items():
        setattr(book, f, v)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def delete_book(db: Session, book_id: int) -> None:
    book = db.get(Book, book_id)
    db.delete(book)
    db.commit()


def get_incoming_requests(db: Session, user_id: int) -> List[ShareRequest]:
    return db.exec(
        select(ShareRequest)
        .where(ShareRequest.receiver_id == user_id)
        .options(
            selectinload(ShareRequest.sender),
            selectinload(ShareRequest.suggested_book).selectinload(Book.info).selectinload(BookInfo.tags),
            selectinload(ShareRequest.received_book).selectinload(Book.info).selectinload(BookInfo.tags),
        )
    ).all()

def get_outgoing_requests(db: Session, user_id: int) -> List[ShareRequest]:
    return db.exec(
        select(ShareRequest)
        .where(ShareRequest.sender_id == user_id)
        .options(
            selectinload(ShareRequest.receiver),
            selectinload(ShareRequest.suggested_book).selectinload(Book.info).selectinload(BookInfo.tags),
            selectinload(ShareRequest.received_book).selectinload(Book.info).selectinload(BookInfo.tags),
        )
    ).all()

def create_share_request(db: Session, sr: schemas.ShareRequestCreate, sender_id: int) -> ShareRequest:
    req = ShareRequest(
        sender_id=sender_id,
        receiver_id=sr.receiver_id,
        suggested_book_id=sr.suggested_book_id,
        received_book_id=sr.received_book_id,
        status="pending",
        requested_date=datetime.utcnow().date()
    )
    db.add(req); db.commit(); db.refresh(req)
    return req

def respond_request(db: Session, req_id: int, approve: bool) -> ShareRequest:
    req = db.get(ShareRequest, req_id)
    req.status = "accepted" if approve else "declined"
    db.add(req); db.commit(); db.refresh(req)
    return req

def delete_request(db: Session, req_id: int) -> None:
    req = db.get(ShareRequest, req_id)
    db.delete(req); db.commit()