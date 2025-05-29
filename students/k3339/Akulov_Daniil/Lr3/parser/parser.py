from bs4 import BeautifulSoup
from models import Hackathon
from datetime import datetime, timedelta

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('LAB1_DB_URL')
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

html_paths = {
    "title": '#rec488755787 > div > div > div.t-feed__post-popup__container.t-container.t-popup__container.t-popup__container-static > div.t-feed__post-popup__content-wrapper > div:nth-child(3) > div.t-feed__post-popup__title-wrapper > h1',
    'description': '#feed-text > div > section > div > div:nth-child(1)'
}


def _get_text_from_html(tag, default_text):
    return tag.text.strip() if tag else default_text


def parse_page(html_data):
    bs = BeautifulSoup(html_data, 'lxml')
    title_tag = bs.select_one(html_paths.get('title'))
    title = _get_text_from_html(title_tag, "No title")
    description_tag = bs.select_one(html_paths.get('description'))
    description = _get_text_from_html(description_tag, "No description")
    return {'title': title, 'description': description}


def parse_and_save_page(html_data):
    data = parse_page(html_data)
    session = SessionLocal()
    try:
        hackathon = Hackathon(
            name=data["title"],
            description=data["description"],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
        )
        session.add(hackathon)
        session.commit()
        session.refresh(hackathon)
        return hackathon
    finally:
        session.close()
