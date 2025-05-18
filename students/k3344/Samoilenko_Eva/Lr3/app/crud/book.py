from typing import List

from fastapi import Depends, HTTPException, APIRouter
from ..db.connection import get_session
from sqlmodel import select
# from celery.result import AsyncResult

# from ..tasks import parse_url_task
from ..models.book import Book
from ..models.profile import Profile
from ..models.profileLibrary import ProfileLibrary
from ..schemas.book import BookBase

router = APIRouter()


# Получить список всех книг из разных библиотек
@router.get("/library", response_model=List[Book])
def get_books(session=Depends(get_session)):
    return session.exec(select(Book)).all()


# Добавить новую книгу в библиотеку профиля
@router.post("/profiles/{profile_id}/library/books", response_model=Book)
def add_book_to_library(profile_id: int, book_data: BookBase, session=Depends(get_session)):
    library = session.exec(
        select(ProfileLibrary)
        .where(ProfileLibrary.profile_id == profile_id)).first()

    if library is None:
        raise HTTPException(status_code=404, detail="Library not found")

    new_book = Book(**book_data.model_dump(), profile_library_id=library.id)

    library.books.append(new_book)

    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


PARSER_URL = "http://parser_app:8001"  # имя сервиса из docker-compose


# @router.post("/parse")
# async def parse_url(url: str):
#     try:
#         # задачу в очередь Celery
#         task = parse_url_task.delay(url)
#         return {"task_id": task.id, "status": "Task started"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.get("/task/{task_id}")
# async def get_task_status(task_id: str):
#     task_result = AsyncResult(task_id)
#     return {
#         "task_id": task_id,
#         "status": task_result.status,
#         "result": task_result.result if task_result.ready() else None
#     }
#

# Обновить книгу
@router.patch("/profiles/{profile_id}/library/{book_id}", response_model=Book)
def update_book(profile_id: int, book_id: int, book_data: BookBase, session=Depends(get_session)):
    book = session.get(Book, book_id)
    library = session.exec(
        select(ProfileLibrary)
        .where(ProfileLibrary.profile_id == profile_id)).first()

    if book is None or book.profile_library_id != library.id:
        raise HTTPException(status_code=404, detail="Book not found or does not belong to this "
                                                    "library")

    book_data_dict = book_data.model_dump(exclude_unset=True)
    for key, value in book_data_dict.items():
        setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


# Удалить книгу
@router.delete("/profiles/{profile_id}/library/{book_id}")
def delete_book(profile_id: int, book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    profile = session.get(Profile, profile_id)
    library = session.exec(
        select(ProfileLibrary)
        .where(book.profile_library_id == profile.library.id))

    # if book is None:
    if book is None or book.profile_library_id != library.id:
        raise HTTPException(status_code=404, detail="Book not found or does not belong to this "
                                                    "library")

    session.delete(book)
    session.commit()
    return {"status": 200, "message": "Book deleted successfully"}
