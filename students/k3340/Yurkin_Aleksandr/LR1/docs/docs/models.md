# Модели

В данном разделе описаны модели, используемые в проекте.

## Пользователь (User)

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None

    trips_created: List[Trip] = Relationship(back_populates="creator")
    trips_joined: List[Trip] = Relationship(back_populates="participants", link_model=TripParticipant)
    reviews: List[Review] = Relationship(back_populates="user")
    messages: List[Message] = Relationship(back_populates="user")
```

## Поездка (Trip)

```python
class TripDefault(SQLModel):
    title: str
    departure: str
    destination: str
    start_date: date
    end_date: date
    description: Optional[str] = None

class Trip(TripDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="user.id")
    creator: Optional[User] = Relationship(back_populates="trips_created")
    participants: List[User] = Relationship(back_populates="trips_joined", link_model=TripParticipant)
    reviews: List[Review] = Relationship(back_populates="trip")
    messages: List[Message] = Relationship(back_populates="trip")
```

## Ассоциативная сущность – участники поездки (TripParticipant)

```python
class TripParticipant(SQLModel, table=True):
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    status: str = Field(default="pending")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
```

## Отзыв (Review)

```python
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    user_id: int = Field(foreign_key="user.id")
    rating: int
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Сообщение (Message)


```python
class MessageDefault(SQLModel):
    content: str

class Message(MessageDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    trip: Optional["Trip"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")

class MessageDetails(MessageDefault):
    id: int
    created_at: datetime
    trip: Optional["Trip"] = None
    user: Optional["User"] = None
```

