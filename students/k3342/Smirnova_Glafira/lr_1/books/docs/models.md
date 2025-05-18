# ORM-модели для Bookcrossing App

В этом документе представлены все ORM-модели проекта, их поля и связи между ними.

Модели были реализованы с помощью бибилиотеки SQLModel.


---

## User

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    age: int | None = Field(default=None)
    info: str | None = Field(default=None)

    ownerships: List["Ownership"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    books: List["Book"] = Relationship(
            back_populates="users",
            link_model=Ownership,
            sa_relationship_kwargs={"overlaps": "ownerships,user,book"}
        )
```

Представляет пользователя. Имеет уникальные `username` и `email`.  
Связан с `Ownership` один-ко-многим, что определяет, какими книгами он владеет.
Связан с `Book` многие-ко-многим через `Ownership`.

---

## Book

```python
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    author: str
    year: int
    publisher: str

    genres: List["Genre"] = Relationship(
        back_populates="books",
        link_model=BookGenre
    )
    ownerships: List["Ownership"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    users: List[User] = Relationship(
        back_populates="books",
        link_model=Ownership,
        sa_relationship_kwargs={"overlaps": "ownerships,book,user"}
    )
```

Описание книги. Связана с жанрами и юзерами (многие-ко-многим) и с фактами владения этой книгой (один-ко-многим).

---

## Genre

```python
class Genre(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    books: List["Book"] = Relationship(
        back_populates="genres",
        link_model=BookGenre
    )
```

Жанр книги (например, Fantasy, Drama).  
Многие книги могут принадлежать многим жанрам (many-to-many).
Заполняются дефолтными значениями при первой инициализации БД.

---

## BookGenre (связь книги и жанра)

```python
class BookGenre(SQLModel, table=True):
    book_id: int = Field(foreign_key="book.id", primary_key=True, index=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True, index=True)
```

Связывающая таблица many-to-many между книгами и жанрами.

---

## Ownership

```python
class Ownership(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    is_current: bool = Field(default=True)

    user: User = Relationship(back_populates="ownerships")
    book: Book = Relationship(back_populates="ownerships")

    offer: Optional["Offer"] = Relationship(
        back_populates="ownership",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

Определяет владение книгой: кто владеет, чем, и является ли это владение активным.
Является связующей таблицей между юзером и книгой.
Имеет один-к-одному связь с Оффером. При удалении Владения, Оффер также удаляется.

---

## Offer

```python
class Offer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ownership_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("ownership.id", ondelete="CASCADE"),
            unique=True,
            index=True
        )
    )
    is_open: bool = Field(default=True)
    comment: str | None = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ownership: Ownership = Relationship(back_populates="offer")
```

Оффер на обмен конкретной книги.  
Каждому `Ownership` может соответствовать только один `Offer`.

---

## SwapRequest

```python
class SwapRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    get_offer_id: int = Field(foreign_key="offer.id", index=True)
    give_offer_id: int = Field(foreign_key="offer.id", index=True)
    comment: str | None = Field(default=None)
    status: SwapStatus = Field(default=SwapStatus.PENDING)

    get_offer: Offer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SwapRequest.get_offer_id"}
    )
    give_offer: Offer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SwapRequest.give_offer_id"}
    )
```

Представляет заявку на обмен конкретными книгами.  
Пользователь предлагает свою книгу (`give_offer`) в обмен на `get_offer`.

Статус заявки определен через Enum:

```python
class SwapStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    outdated = "outdated"
```

---

## Deal

```python
class Deal(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    swap_id: int = Field(foreign_key="swaprequest.id", index=True)
    date_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    swap_request: SwapRequest = Relationship()
```

Фиксирует успешный обмен между двумя пользователями и его время.


