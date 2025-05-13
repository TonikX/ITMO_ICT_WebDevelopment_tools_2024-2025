from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from datetime import datetime, timedelta
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.connection import init_db, get_session
from app.models import (
    UserProfile, UserCreate,
    Trip, TripCreate,
    TripParticipantLink,
    ItineraryItem, ItineraryItemCreate,
    Message, MessageCreate
)
import hashlib
import jwt

# jwt
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app = FastAPI()

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
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_session)) -> UserProfile:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.get(UserProfile, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Аутентификация
@app.post("/register", response_model=UserProfile)
def register(
        user: UserCreate,
        session=Depends(get_session)
):
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
    db_user.hashed_password = hashed  # не сохраняется в БД, для примера
    return db_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          session=Depends(get_session)
          ):
    statement = select(UserProfile).where(UserProfile.username == form_data.username)
    user = session.exec(statement).first()
    if not user or hash_password(form_data.password) != user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

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