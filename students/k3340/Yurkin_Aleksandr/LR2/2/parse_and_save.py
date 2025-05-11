from datetime import timedelta

import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
from models import *

db_url = 'postgresql://tripuser:12345678@localhost:8432/trips'
engine = create_engine(db_url, echo=True)
SQLModel.metadata.create_all(engine)


def parse(response):
    soup = BeautifulSoup(response.text, 'html.parser')

    country = soup.find_all('a', itemprop='item')[1].get_text(strip=True)
    print(country)

    hotels_elements = soup.find_all('p', class_='HotelTitle_descriptionTitle___uwHg')
    hotels = [hotel.text for hotel in hotels_elements]
    print(hotels)

    return country, hotels


def save(country_name, hotels):
    with Session(engine) as session:
        stmt = select(Country).where(Country.name == country_name)
        country = session.exec(stmt).first()
        if not country:
            country = Country(name=country_name)
            session.add(country)
            session.commit()
            session.refresh(country)

        for hotel in hotels:
            trip = Trip(
                title=hotel,
                destination=country_name,
                country_id=country.id,
            )
            session.add(trip)

        session.commit()


def parse_and_save(url):
    response = requests.get(url)
    country, hotels = parse(response)
    save(country, hotels)


parse_and_save("https://sletat.ru/tours/turkey/")
