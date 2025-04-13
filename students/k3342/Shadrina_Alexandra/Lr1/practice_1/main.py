from fastapi import FastAPI

from models import *
from typing_extensions import TypedDict

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, Alexandra!"


@app.get("/users")
def users_list() -> List[User]:
    return temp_users_db


@app.get("/user/{user_id}")
def get_user(user_id: int) -> List[User]:
    return [user for user in temp_users_db if user.get("id") == user_id]


@app.post("/user")
def add_user(user: User) -> TypedDict('Response', {"status": int, "data": User}):
    user_to_append = user.model_dump()
    temp_users_db.append(user_to_append)
    return {"status": 200, "data": user}


@app.delete("/user/delete{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(temp_users_db):
        if user.get("id") == user_id:
            temp_users_db.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/user{user_id}")
def update_user(user_id: int, user: User) -> List[User]:
    for existing_user in temp_users_db:
        if existing_user.get("id") == user_id:
            user_to_append = user.model_dump()
            temp_users_db.remove(existing_user)
            temp_users_db.append(user_to_append)
    return temp_users_db


@app.post("/user/{user_id}/add_book")
def add_book_to_user(user_id: int, book: Book):
    for user in temp_users_db:
        if user.get("id") == user_id:
            book_to_append = book.model_dump()
            user.get("books").append(book_to_append)
            return {"status": 200, "message": "Book added successfully", "data": book}
    return {"status": 404, "message": "User not found"}


@app.put("/user/{user_id}/update_book/{book_id}")
def update_book(user_id: int, book_id: int, book: Book):
    for user in temp_users_db:
        if user.get("id") == user_id:
            for existing_book in user.get("books"):
                if existing_book.get("id") == book_id:
                    existing_book.update(book.dict())
                    return {"status": 200, "message": "Book updated successfully", "data": existing_book}
    return {"status": 404, "message": "User or book not found"}


@app.delete("/user/{user_id}/delete_book/{book_id}")
def delete_book(user_id: int, book_id: int):
    for user in temp_users_db:
        if user.get("id") == user_id:
            for i, book in enumerate(user.get("books")):
                if book.get("id") == book_id:
                    user.get("books").pop(i)
                    return {"status": 200, "message": "Book deleted successfully"}
    return {"status": 404, "message": "User or book not found"}


temp_users_db = [
    {
        "id": 1,
        "username": "booklover92",
        "profile": {"full_name": "Alice Johnson", "email": "alice@example.com"},
        "books": [
            {"id": 101, "title": "1984", "author": "George Orwell"},
            {"id": 102, "title": "Brave New World", "author": "Aldous Huxley"}
        ]
    },
    {
        "id": 2,
        "username": "reader123",
        "profile": {"full_name": "Bob Smith", "email": "bob@example.com"},
        "books": [
            {"id": 103, "title": "Dune", "author": "Frank Herbert"}
        ]
    }
]
