from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.dependencies.auth import get_current_user
from app.db.session import get_session
from app.models.models import Genre
from app.schemas.book import GenreRead

router = APIRouter()

@router.get("/", response_model=list[GenreRead])
def get_all_genres(session: Session = Depends(get_session), _: int = Depends(get_current_user)) -> list[Genre]:
    """Возвращает все жанры с их ID."""
    statement = select(Genre)
    genres = session.exec(statement).all()
    return genres
