# Парсинг и работа с БД

Для парсинга был выбран сайт https://ru.wikipedia.org/. А именно:

```python
urls = [
    https://ru.wikipedia.org/wiki/Аббадия_(замок),
    https://ru.wikipedia.org/wiki/Арагонский_замок_(Реджо-ди-Калабрия),
    https://ru.wikipedia.org/wiki/Арко_(замок),
    https://ru.wikipedia.org/wiki/Барди_(замок),
    https://ru.wikipedia.org/wiki/Башня_Ванга,
    https://ru.wikipedia.org/wiki/Замок_Буонконсильо,
    https://ru.wikipedia.org/wiki/Виголено_(замок),
    https://ru.wikipedia.org/wiki/Галерея_Виктора_Эммануила_II,
    https://ru.wikipedia.org/wiki/Дорога_любви,
    https://ru.wikipedia.org/wiki/Ломбардо,_Розалия,
    https://ru.wikipedia.org/wiki/Маростикский_праздник_шахмат,
    https://ru.wikipedia.org/wiki/Мегалитическое_лицо_в_Борцоне,
    https://ru.wikipedia.org/wiki/Павоне-Канавезе_(замок),
    https://ru.wikipedia.org/wiki/Палаццо_делле_Альбере,
    https://ru.wikipedia.org/wiki/Палаццо_Комунале_(Форли),
    https://ru.wikipedia.org/wiki/Площадь_Саффи,
    https://ru.wikipedia.org/wiki/Пьяцца-делла-Чистерна,
    https://ru.wikipedia.org/wiki/Пьяцца-дель-Дуомо_(Сан-Джиминьяно),
    https://ru.wikipedia.org/wiki/Рокка-Калашио_(замок),
    https://ru.wikipedia.org/wiki/Савойя_(замок),
    https://ru.wikipedia.org/wiki/Собор_Сан-Джиминьяно,
    https://ru.wikipedia.org/wiki/Тироль_(замок),
    https://ru.wikipedia.org/wiki/Торре_Росса,
    https://ru.wikipedia.org/wiki/Торрекьяра_(замок),
    https://ru.wikipedia.org/wiki/Цитадель_Равальдино,
    https://ru.wikipedia.org/wiki/Энн_(замок),
]
```
## Код
DB
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', "postgresql+asyncpg://username:password@localhost/dbname")

engine = create_async_engine(db_url, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

Models
```python
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import date, datetime

class OrganizerBase(SQLModel):
    name: str
    email: str

class OrganizerProfile(OrganizerBase, table=True):
    __tablename__ = "organizerprofile"
    id: int = Field(default=None, primary_key=True)
    trips: List["Trip"] = Relationship(back_populates="organizer")

class OrganizerCreate(OrganizerBase):
    pass

class OrganizerRead(OrganizerBase):
    id: int

class TripBase(SQLModel):
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class Trip(TripBase, table=True):
    __tablename__ = "trip"
    id: int = Field(default=None, primary_key=True)

    organizer_profile_id: Optional[int] = Field(default=None, foreign_key="organizerprofile.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="trips")
    organizer: Optional["OrganizerProfile"] = Relationship(back_populates="trips")
    trip_requests: List["TripRequest"] = Relationship(back_populates="trip")
    saved_by_users: List["SavedTrip"] = Relationship(back_populates="trip")

class TripCreate(TripBase):
    organizer_profile_id: int
    user_id: Optional[int] = None

class TripRead(TripBase):
    id: int
    organizer_profile_id: Optional[int]
    user_id: Optional[int]

class UserBase(SQLModel):
    name: str
    email: str
    preferences: Optional[str] = None
    bio: Optional[str] = None

class User(UserBase, table=True):
    __tablename__ = "user"
    id: int = Field(default=None, primary_key=True)

    trips: List["Trip"] = Relationship(back_populates="user")
    trip_requests: List["TripRequest"] = Relationship(back_populates="user")
    saved_trips: List["SavedTrip"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class TripRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"

class TripRequestBase(SQLModel):
    status: TripRequestStatus = Field(default=TripRequestStatus.pending)

class TripRequest(TripRequestBase, table=True):
    __tablename__ = "triprequest"
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    trip_id: int = Field(foreign_key="trip.id")

    user: "User" = Relationship(back_populates="trip_requests")
    trip: "Trip" = Relationship(back_populates="trip_requests")

class TripRequestCreate(TripRequestBase):
    user_id: int
    trip_id: int

class TripRequestRead(TripRequestBase):
    id: int
    user_id: int
    trip_id: int

class TripUpdate(SQLModel):
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    organizer_profile_id: Optional[int] = None
    user_id: Optional[int] = None

class SavedTripWithDetails(BaseModel):
    trip_id: int
    user_id: int
    saved_at: date
    trip: TripRead

    class Config:
        orm_mode = True

class UserRead(UserBase):
    id: int
    trips: List[TripRead]
    trip_requests: List[TripRequestRead]
    saved_trips: List[SavedTripWithDetails]

class TripRequestWithDetails(TripRequestRead):
    trip: Optional[TripRead]
    user: Optional[UserRead]

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[str] = None
    bio: Optional[str] = None

class TripWithDetails(TripRead):
    user: Optional[UserRead]
    organizer: Optional[OrganizerRead]

class SavedTrip(SQLModel, table=True):
    __tablename__ = "savedtrip"
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)

    saved_at: Optional[date] = Field(default_factory=date.today)

    user: "User" = Relationship(back_populates="saved_trips")
    trip: "Trip" = Relationship(back_populates="saved_by_users")

class MessageBase(BaseModel):
    content: str

    class Config:
        orm_mode = True

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    trip_id: int = Field(foreign_key="trip.id")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    sender: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Message.sender_id]"})
    receiver: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Message.receiver_id]"})
    trip: "Trip" = Relationship()

class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int
    trip_id: int

class MessageRead(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    trip_id: int
    timestamp: datetime

class MessageUpdate(MessageBase):
    content: Optional[str] = None

class SaveTripRequest(BaseModel):
    user_id: int
    trip_id: int

class SavedTripDelete(BaseModel):
    user_id: int
    trip_id: int
```

## Результаты

* Threading
```python
import threading
import requests
from bs4 import BeautifulSoup
from db import get_session
from models import Trip
import time

def load_urls(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def parse_and_save(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find('h1', id='firstHeading')
        destination = title_element.get_text(strip=True) if title_element else "Неизвестно"

        description = ""
        for p in soup.find('div', class_='mw-parser-output').find_all('p'):
            text = p.get_text(strip=True)
            if text:
                description += text + " "
                if len(description) > 1000:
                    break
        if not description.strip():
            description = "Описание отсутствует."

        with get_session() as session:
            session.add(Trip(destination=destination, description=description))
            session.commit()
        print(f"[Thread] {destination} сохранена.")

    except Exception as e:
        print(f"[Thread Error] {url}: {e}")

def handle_url_threading(chunk):
    for url in chunk:
        parse_and_save(url)

def main():
    urls = load_urls("urls.txt")
    num_threads = 5
    step = len(urls) // num_threads
    threads = []

    for i in range(num_threads):
        start = i * step
        end = len(urls) if i == num_threads - 1 else (i + 1) * step
        t = threading.Thread(target=handle_url_threading, args=(urls[start:end],))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Время выполнения: {time.time() - start:.2f} сек")
```

```python
Время выполнения: 1.42 сек
```

* Multiprocessing
```python
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from db import get_session
from models import Trip

def load_urls(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def parse_and_save(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find('h1', id='firstHeading')
        destination = title_element.get_text(strip=True) if title_element else "Неизвестно"

        description = ""
        content_div = soup.find('div', class_='mw-parser-output')
        if content_div:
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    description += text + " "
                    if len(description) > 1000:
                        break

        if not description.strip():
            description = "Описание отсутствует."

        with get_session() as session:
            session.add(Trip(destination=destination, description=description))
            session.commit()
        print(f"[Process] {destination} сохранена.")
    except Exception as e:
        print(f"[Process Error] {url}: {e}")

def handle_url_multi(chunk):
    for url in chunk:
        parse_and_save(url)

def main():
    urls = load_urls("urls.txt")
    num_processes = 5
    chunk_size = len(urls) // num_processes
    chunks = [urls[i * chunk_size: (i + 1) * chunk_size] for i in range(num_processes - 1)]
    chunks.append(urls[(num_processes - 1) * chunk_size:])

    with Pool(processes=num_processes) as pool:
        pool.map(handle_url_multi, chunks)

if __name__ == "__main__":
    import time

    start = time.time()
    main()
    print(f"Время выполнения: {time.time() - start:.2f} сек")
```

```python
Время выполнения: 2.07 сек
```

* Async
```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from db import get_session
from models import Trip

def load_urls(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

async def fetch(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return await response.text(), url
    except Exception as e:
        print(f"[Fetch Error] {url}: {e}")
        return "", url

async def parse_and_save(html, url):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_element = soup.find('h1', id='firstHeading')
        destination = title_element.get_text(strip=True) if title_element else "Неизвестно"

        description = ""
        content_div = soup.find('div', class_='mw-parser-output')
        if content_div:
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    description += text + " "
                    if len(description) > 1000:
                        break

        if not description.strip():
            description = "Описание отсутствует."

        with get_session() as session:
            session.add(Trip(destination=destination, description=description))
            session.commit()
        print(f"[Async] {destination} сохранена.")
    except Exception as e:
        print(f"[Async Error] {url}: {e}")

async def handle_url_async(chunk):
    async with aiohttp.ClientSession() as session:
        htmls = await asyncio.gather(*(fetch(session, url) for url in chunk))
        await asyncio.gather(*(parse_and_save(html, url) for html, url in htmls if html))

async def main():
    urls = load_urls("urls.txt")
    num_chunks = 5
    chunk_size = len(urls) // num_chunks
    chunks = [urls[i * chunk_size: (i + 1) * chunk_size] for i in range(num_chunks - 1)]
    chunks.append(urls[(num_chunks - 1) * chunk_size:])
    await asyncio.gather(*(handle_url_async(chunk) for chunk in chunks))

if __name__ == "__main__":
    import time

    start = time.time()
    asyncio.run(main())
    print(f"Время выполнения: {time.time() - start:.2f} сек")
```

```python
Время выполнения: 0.11 сек
```

# Вывод

Можно попробовать сделать вывод, что эффективнее всего асинхронный подход, но было, возможно, мало данных для парсинга.
