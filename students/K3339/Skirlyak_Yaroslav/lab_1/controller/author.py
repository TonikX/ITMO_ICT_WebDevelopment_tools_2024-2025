from typing import List
from fastapi import HTTPException, Depends, APIRouter, status
from sqlmodel import select, Session
from connection import get_session
from models import Author, AuthorOut, AuthorIn
from contextlib import contextmanager

router = APIRouter(prefix="/authors", tags=["Authors"])


@contextmanager
def session_manager(session: Session):
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        session.close()


@router.get("", response_model=List[AuthorOut])
def authors_list(session: Session = Depends(get_session)):
    with session_manager(session):
        authors = session.exec(select(Author)).all()
        return authors


@router.get("/{author_id}", response_model=AuthorOut)
def author_get(author_id: int, session: Session = Depends(get_session)):
    with session_manager(session):
        author = session.get(Author, author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        return author


@router.post("", response_model=AuthorOut, status_code=status.HTTP_201_CREATED)
def author_create(author: AuthorIn, session: Session = Depends(get_session)):
    with session_manager(session):
        db_author = Author.model_validate(author)
        session.add(db_author)
        session.commit()
        session.refresh(db_author)
        return db_author


@router.patch("/{author_id}", response_model=AuthorOut)
def author_update(
        author_id: int,
        updated_author: AuthorIn,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        author = session.get(Author, author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )

        update_data = updated_author.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author, key, value)

        session.add(author)
        session.commit()
        session.refresh(author)
        return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def author_delete(author_id: int, session: Session = Depends(get_session)):
    with session_manager(session):
        author = session.get(Author, author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        session.delete(author)
        session.commit()
        return None