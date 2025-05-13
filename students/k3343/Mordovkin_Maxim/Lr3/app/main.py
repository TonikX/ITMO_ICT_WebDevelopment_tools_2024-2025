import os
import requests
from fastapi import HTTPException
from fastapi import FastAPI, Depends, HTTPException
from app.tasks import parse_url_task
from celery.result import AsyncResult
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
from sqlmodel import select, Session
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from app.auth import verify_jwt, verify_password, create_jwt, hash_password
from app.connection import init_db, get_session
from app.models import (
    UserProfile, UserCreate,
    Trip, TripCreate,
    TripParticipantLink,
    ItineraryItem, ItineraryItemCreate,
    Message, MessageCreate, ChangePassword, Page
)
import jwt
from pydantic import BaseModel, HttpUrl


class ParseRequest(BaseModel):
    url: HttpUrl

PARSER_URL = os.getenv("PARSER_URL", "http://localhost:8001/parse")


# jwt
SECRET_KEY = "9f8aC3nVgB1rX5dZ7qW2LkE0mJsRtY4uAaTbHpN6xOiVzPgQeChMwKldUFyXEr39"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app = FastAPI()
http_bearer = HTTPBearer()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# инициализация бд
@app.on_event("startup")
def on_startup():
    init_db()

# хэширование паролей и генерация токенов
# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: Session = Depends(get_session)
) -> UserProfile:
    """
    Извлекаем пользователя по JWT-токену из заголовка Authorization: Bearer <token>.
    """
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    user = session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Аутентификация
@app.post("/register", response_model=UserProfile)
def register(
        user: UserCreate,
        session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(UserProfile).where(UserProfile.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = hash_password(user.password)
    db_user = UserProfile(
        username=user.username,
        hashed_password=hashed,
        full_name=user.full_name,
        bio=user.bio,
        preferences=user.preferences
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/login")
def login(
    user_in: UserCreate,
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(UserProfile).where(UserProfile.username == user_in.username)
    ).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# получения данных текущего пользователя
@app.get("/users/me", response_model=UserProfile)
def read_current_user(current_user: UserProfile = Depends(get_current_user)):
    """
    Возвращаем текущего авторизованного пользователя
    """
    return current_user

# получение списка всех пользователей
@app.get("/users", response_model=List[UserProfile])
def list_users(session=Depends(get_session)):
    return session.exec(select(UserProfile)).all()

# смена пароля текущего пользователя
@app.post("/users/me/password")
def change_password(
        passwords: ChangePassword,
        current_user: UserProfile = Depends(get_current_user),
        session=Depends(get_session)
):

    # проверка old пароля
    if not verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # установка new пароля
    current_user.hashed_password = hash_password(passwords.new_password)
    session.add(current_user)
    session.commit()
    return {"status": "password_changed"}





# CRUD поездок
@app.post("/trips", response_model=Trip)
def create_trip(trip: TripCreate, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    db_trip = Trip(**trip.dict(), owner_id=current_user.id)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip

@app.get("/trips", response_model=List[Trip])
def list_trips(session=Depends(get_session)):
    return session.exec(select(Trip)).all()

@app.get("/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: int, session=Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.patch("/trips/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, trip_data: TripCreate, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip or db_trip.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found or access denied")
    update_data = trip_data.dict(exclude_unset=True)
    for key, val in update_data.items():
        setattr(db_trip, key, val)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip or db_trip.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found or access denied")
    session.delete(db_trip)
    session.commit()
    return {"status": "deleted"}

# Управление участниками поездки
@app.post("/trips/{trip_id}/join")
def join_trip(trip_id: int, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    link = TripParticipantLink(trip_id=trip_id, user_id=current_user.id, joined_at=str(datetime.utcnow()))
    session.add(link)
    session.commit()
    return {"status": "joined"}

@app.delete("/trips/{trip_id}/leave")
def leave_trip(trip_id: int, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    link = session.get(TripParticipantLink, (trip_id, current_user.id))
    if not link:
        raise HTTPException(status_code=404, detail="Not a participant")
    session.delete(link)
    session.commit()
    return {"status": "left"}

# Эндпоинты для маршрута (itinerary)
@app.post("/trips/{trip_id}/itinerary", response_model=ItineraryItem)
def create_itinerary_item(trip_id: int, item: ItineraryItemCreate, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip or trip.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    db_item = ItineraryItem(**item.dict(), trip_id=trip_id)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@app.get("/trips/{trip_id}/itinerary", response_model=List[ItineraryItem])
def list_itinerary(trip_id: int, session=Depends(get_session)):
    statement = select(ItineraryItem).where(ItineraryItem.trip_id == trip_id)
    return session.exec(statement).all()

@app.delete("/trips/{trip_id}/itinerary/{item_id}")
def delete_itinerary_item(trip_id: int, item_id: int, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    db_item = session.get(ItineraryItem, item_id)
    if not db_item or db_item.trip_id != trip_id:
        raise HTTPException(status_code=404, detail="Item not found")
    trip = session.get(Trip, trip_id)
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    session.delete(db_item)
    session.commit()
    return {"status": "deleted"}

# Эндпоинты для сообщений
@app.post("/trips/{trip_id}/messages", response_model=Message)
def post_message(trip_id: int, msg: MessageCreate, current_user: UserProfile = Depends(get_current_user), session=Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_msg = Message(**msg.dict(), trip_id=trip_id, sender_id=current_user.id, timestamp=str(datetime.utcnow()))
    session.add(db_msg)
    session.commit()
    session.refresh(db_msg)
    return db_msg

@app.get("/trips/{trip_id}/messages", response_model=List[Message])
def list_messages(trip_id: int, session=Depends(get_session)):
    statement = select(Message).where(Message.trip_id == trip_id)
    return session.exec(statement).all()


@app.post("/parse-url")
def parse_url(
    req: ParseRequest,
    # Если хотите оставить авторизацию, можно добавить Depends(get_current_user)
    session=Depends(get_session),              # если нужен доступ к БД
    current_user: UserProfile = Depends(get_current_user)  # если маршрут только для авторизованных
):
    """
    Получает JSON {"url": "..."}, делает POST к отдельному сервису-парсеру
    (PARSER_URL), и возвращает клиенту ответ парсера.
    """
    # Формируем JSON, как ожидает парсер: {"url": "<строка>"}
    payload = {"url": str(req.url)}

    try:
        response = requests.post(PARSER_URL, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Если парсер недоступен или вернул ошибку
        raise HTTPException(
            status_code=502,
            detail=f"Не удалось получить ответ от сервиса-парсера: {e}"
        )

    # Если всё ок, возвращаем JSON, который вернул парсер
    return response.json()

class AsyncParseResponse(BaseModel):
    task_id: str
    status: str

@app.post("/parse-async", response_model=AsyncParseResponse)
def parse_url_async(
    req: ParseRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Принимает JSON {"url": "..."}, создаёт Celery-задачу parse_url_task.delay(url)
    и возвращает ID этой задачи, чтобы клиент мог отслеживать прогресс.
    """
    task = parse_url_task.delay(str(req.url))
    return {"task_id": task.id, "status": "queued"}

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None

@app.get("/task-status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """
    Возвращает текущий статус Celery-задачи (PENDING, SUCCESS, FAILURE и т.д.),
    а также результат, если задача завершена.
    """
    res = AsyncResult(task_id, app=parse_url_task.app)  # или celery_app.celery
    state = res.state
    response = {"task_id": task_id, "status": state, "result": None, "error": None}

    if state == "SUCCESS":
        # Результат – это JSON, который вернул парсер
        response["result"] = res.result
    elif state == "FAILURE":
        # Собираем информацию об ошибке
        response["error"] = str(res.result)
    # В других состояниях (PENDING, STARTED, RETRY) результата нет
    return response