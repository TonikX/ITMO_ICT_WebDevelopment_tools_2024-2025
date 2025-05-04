from fastapi import FastAPI
from typing import List

from models import Trip

app = FastAPI()


@app.get("/trips/", response_model=List[Trip])
def get_all_trips():
    return temp_trips_db


@app.get("/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: int):
    for trip in temp_trips_db:
        if trip["id"] == trip_id:
            return trip
    return {"error": "Trip not found"}


@app.post("/trip")
def add_trip(trip: Trip):
    temp_trips_db.append(trip.dict())
    return {"status": 200, "data": trip}


@app.delete("/trip/delete/{trip_id}")
def delete_trip(trip_id: int):
    for i, trip in enumerate(temp_trips_db):
        if trip.get("id") == trip_id:
            temp_trips_db.pop(i)
            return {"status": 201, "message": "Trip deleted"}
    return {"status": 404, "message": "Trip not found"}


@app.put("/trip/{trip_id}")
def update_trip(trip_id: int, trip: Trip):
    for i, t in enumerate(temp_trips_db):
        if t.get("id") == trip_id:
            temp_trips_db[i] = trip.dict()
            return {"status": 200, "data": trip}
    return {"status": 404, "message": "Trip not found"}


temp_trips_db = [
    {
        "id": 1,
        "title": "Поездка в Грузию",
        "organizer_name": "Иван Петров",
        "start_location": "Москва",
        "end_location": "Тбилиси",
        "start_date": "2025-06-10",
        "end_date": "2025-06-25",
        "organizer_profile": {
            "id": 1,
            "bio": "Люблю горы и походы",
            "experience": "5 лет путешествий автостопом",
            "travel_preferences": "Пешие маршруты, палатки"
        },
        "participants": [
            {
                "id": 1,
                "name": "Ольга Иванова",
                "message": "Ищу компанию для похода по Кавказу"
            },
            {
                "id": 2,
                "name": "Антон Смирнов",
                "message": "Уже был в Грузии, могу быть проводником"
            }
        ]
    },
    {
        "id": 2,
        "title": "Тур по Алтаю",
        "organizer_name": "Мария Козлова",
        "start_location": "Новосибирск",
        "end_location": "Горно-Алтайск",
        "start_date": "2025-07-01",
        "end_date": "2025-07-10",
        "organizer_profile": {
            "id": 2,
            "bio": "Преподаватель йоги",
            "experience": "Организация ретритов",
            "travel_preferences": "Медитация, природа, эко-поездки"
        },
        "participants": []
    }
]
