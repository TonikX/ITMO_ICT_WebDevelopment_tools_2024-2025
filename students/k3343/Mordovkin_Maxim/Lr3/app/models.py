from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# Ассоциативная таблица для участников поездки
class TripParticipantLink(SQLModel, table=True):
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="userprofile.id", primary_key=True)
    joined_at: Optional[str]


# Сущность для пункта маршрута (itinerary)
class ItineraryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id")
    day_number: int
    location: str
    description: Optional[str]

    trip: Optional["Trip"] = Relationship(back_populates="itinerary_items")


# Сущность сообщений внутри поездки
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id")
    sender_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")
    content: str
    timestamp: Optional[str]

    trip: Optional["Trip"] = Relationship(back_populates="messages")
    sender: Optional["UserProfile"] = Relationship(back_populates="sent_messages")


# Основная таблица пользователей
class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=256)
    username: str = Field(index=True, unique=True)
    full_name: Optional[str]
    bio: Optional[str]
    preferences: Optional[str]

    # Поездки, созданные пользователем (one-to-many)
    trips: List["Trip"] = Relationship(back_populates="owner")

    # Поездки, в которых пользователь участвует (many-to-many)
    joined_trips: List["Trip"] = Relationship(
        back_populates="participants", link_model=TripParticipantLink
    )

    # Отправленные сообщения (one-to-many)
    sent_messages: List[Message] = Relationship(back_populates="sender")


# Основная таблица поездок
class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    start_date: str
    end_date: str
    origin: str
    destination: str
    duration_days: Optional[int]
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")

    # Владелец поездки (one-to-many)
    owner: Optional[UserProfile] = Relationship(back_populates="trips")

    # Участники поездки (many-to-many)
    participants: List[UserProfile] = Relationship(
        back_populates="joined_trips", link_model=TripParticipantLink
    )

    # Пункты маршрута (one-to-many)
    itinerary_items: List[ItineraryItem] = Relationship(back_populates="trip")

    # Сообщения внутри поездки (one-to-many)
    messages: List[Message] = Relationship(back_populates="trip")


# Новая таблица для сохранённых страниц (pages)
class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str]


# DTO-модели для создания сущностей
class UserCreate(SQLModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[str] = None
    password: str  # будет хэшироваться при регистрации


# dto для смены пароля
class ChangePassword(SQLModel):
    old_password: str
    new_password: str


class TripCreate(SQLModel):
    title: str
    description: Optional[str]
    start_date: str
    end_date: str
    origin: str
    destination: str
    duration_days: Optional[int]


class ItineraryItemCreate(SQLModel):
    day_number: int
    location: str
    description: Optional[str]


class MessageCreate(SQLModel):
    content: str
