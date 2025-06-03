# Book
Класс для создания модели 
```python
class BookDefault(SQLModel):
    title: str
    author: str
    genre: Genres
    published_year: int
```
Сама модель
```python
class Book(BookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user_books: List["UserBook"] = Relationship(back_populates="book")
```