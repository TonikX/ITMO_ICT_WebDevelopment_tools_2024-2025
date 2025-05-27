import os

import requests
from alembic.templates.multidb.env import db_names
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
from models import *
import random

db_url = os.getenv('DB_URL', 'postgresql://dbuser:12345678@localhost:25432/db')
engine = create_engine(db_url, echo=True)
SQLModel.metadata.create_all(engine)

# def parse_task(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     title = soup.find('h2', class_='problem_title')
#
#     text = ''
#     texts = soup.find_all('div', class_='problem_par_normal')
#     for t in texts:
#         text += t.text.strip() + '\n'
#
#     return title.text, text

def parse_task(url):
    return f"Mock title {random.randint(1, 1000)}", f"Mock text {random.randint(1, 1000)}"

def save_task(title, text):
    with Session(engine) as session:
        task = Task(
            title=title,
            description=text,
        )
        session.add(task)
        session.commit()

def parse_and_save(url):
    title, text = parse_task(url)
    save_task(title, text)