from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from Lr1.connection import get_session
from Lr1.models import Genre, GenreCreate, GenreRead, GenreUpdate

router = APIRouter(prefix="/genres", tags=["Genres"])

@router.post("/", response_model=GenreRead)
def create_genre(genre: GenreCreate, session: Session = Depends(get_session)):
    db_genre = Genre.model_validate(genre)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre

@router.get("/", response_model=list[GenreRead])
def read_genres(session: Session = Depends(get_session)):
    return session.exec(select(Genre)).all()

@router.get("/{genre_id}", response_model=GenreRead)
def read_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@router.patch("/{genre_id}", response_model=GenreRead)
def update_genre(genre_id: int, genre_update: GenreUpdate, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    for key, value in genre_update.model_dump(exclude_unset=True).items():
        setattr(genre, key, value)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre

@router.delete("/{genre_id}")
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(genre)
    session.commit()
    return {"ok": True}
