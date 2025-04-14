from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from api.models.connection import get_session
from api.models.models import Genre
from api.schemas.genre_schemas import GenreResponse, GenreCreateAndUpdate

genre_router = APIRouter()


@genre_router.get("/genres_get", response_model=List[GenreResponse])
def genres_get(session=Depends(get_session)):
    genres = session.exec(select(Genre)).all()
    if not genres:
        raise HTTPException(status_code=404, detail="Genres not found")
    return genres


@genre_router.post("/genre_post", response_model=GenreResponse)
def genre_post(genre_create: GenreCreateAndUpdate, session=Depends(get_session)):
    genre_db = Genre(**genre_create.dict())

    session.add(genre_db)
    session.commit()
    session.refresh(genre_db)
    return genre_db


@genre_router.patch("/genre_patch{genre_id}", response_model=GenreResponse)
def user_update(genre_id: int, genre_data: GenreCreateAndUpdate, session=Depends(get_session)):
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = genre_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_genre, key, value)

    session.commit()
    session.refresh(db_genre)
    return db_genre


@genre_router.get("/genre_get{genre_id}", response_model=GenreResponse)
def genre_get(genre_id: int, session=Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@genre_router.delete("/genre_delete_{genre_id}")
def genre_delete(genre_id: int, session=Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(genre)
    session.commit()
    return {"ok": True}
