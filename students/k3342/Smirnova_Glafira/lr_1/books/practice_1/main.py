from typing import List, Optional

from fastapi import FastAPI, HTTPException

from practice_1.models import Book, Author

from typing_extensions import TypedDict

app = FastAPI()

temp_db = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "year": 1925,
        "publisher": "Charles Scribner's Sons",
        "author": {
            "id": 1,
            "name": "F. Scott",
            "surname": "Fitzgerald",
            "birth_year": 1896
        },
        "genres": [
            {"id": 1, "name": "Novel"},
            {"id": 2, "name": "Historical"}
        ]
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "year": 1960,
        "publisher": "J.B. Lippincott & Co.",
        "author": {
            "id": 2,
            "name": "Harper",
            "surname": "Lee",
            "birth_year": 1926
        },
        "genres": [
            {"id": 1, "name": "Novel"},
            {"id": 3, "name": "Southern Gothic"}
        ]
    },
    {
        "id": 3,
        "title": "1984",
        "year": 1949,
        "publisher": "Secker & Warburg",
        "author": {
            "id": 3,
            "name": "George",
            "surname": "Orwell",
            "birth_year": 1903
        },
        "genres": [
            {"id": 4, "name": "Dystopian"},
            {"id": 5, "name": "Science Fiction"}
        ]
    }
]

@app.get("/books")
def get_books() -> List[Book]:
    return temp_db

@app.get("/book/{book_id}")
def get_book(book_id: int) -> Optional[Book]:
    for book in temp_db:
        if book["id"] == book_id:
            return book
    return None

@app.post("/book")
def create_book(book: Book) -> TypedDict('Response', {"status": int, "data": Book}):
    temp_db.append(book.model_dump())
    return {"status": 200, "data": book}

@app.delete("/book/{book_id}")
def delete_book(book_id: int) -> TypedDict('Response', {"status": int, "message": str}):
    for i, book in enumerate(temp_db):
        if book["id"] == book_id:
            temp_db.pop(i)
            return {"status": 200, "message": "Book deleted"}
    return {"status": 404, "message": "Book not found"}

@app.put("/book/{book_id}")
def update_book(book_id: int, book: Book) -> List[Book]:
    for i, b in enumerate(temp_db):
        if b["id"] == book_id:
            temp_db[i] = book.model_dump()
            return temp_db
    return temp_db

@app.get("/book/{book_id}/author")
def get_book_author(book_id: int) -> Optional[Author]:
    for book in temp_db:
        if book["id"] == book_id:
            return book.get("author")
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/authors")
def get_all_authors() -> List[Author]:
    authors = []
    seen_ids = set()
    for book in temp_db:
        author = book.get("author")
        if author and author["id"] not in seen_ids:
            authors.append(author)
            seen_ids.add(author["id"])
    return authors

@app.post("/book/{book_id}/author")
def add_author_to_book(book_id: int, author: Author) -> TypedDict('Response', {"status": int, "message": str, 'author': Author}):
    for book in temp_db:
        if book["id"] == book_id:
            book["author"] = author.model_dump()
            return {"status": 200, "message": "Author added", "author": author}
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/book/{book_id}/author")
def delete_book_author(book_id: int) -> TypedDict('Response', {"status": int, "message": str}):
    for book in temp_db:
        if book["id"] == book_id:
            book["author"] = None
            return {"status": 200, "message": "Author deleted"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/book/{book_id}/author")
def update_book_author(book_id: int, author: Author) -> TypedDict('Response', {"status": int, "message": str, 'author': Author}):
    for book in temp_db:
        if book["id"] == book_id:
            book["author"] = author.model_dump()
            return {"status": 200, "message": "Author updated", "author": author}
    raise HTTPException(status_code=404, detail="Book not found")