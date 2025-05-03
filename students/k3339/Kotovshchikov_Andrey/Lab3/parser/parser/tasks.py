import os
import logging

import psycopg
import requests
from bs4 import BeautifulSoup
from celery import Celery
from parser.logger import setup_logger

logger = logging.getLogger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379")


@celery.task(name="parse")
def parse_and_save_async(url: str) -> None:
    setup_logger()

    connection = psycopg.connect(os.getenv("POSTGRES_URL"))
    cursor = connection.cursor()
    logger.info("Connected to database")

    skills: set[str] = set()
    logger.info("Start parse: %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        logger.error("Parse failed: %s", url)
        return

    soup = BeautifulSoup(response.text, features="html.parser")
    title = soup.find("title").text
    logger.info("Page title: %s", title)

    for row in soup.find("table").find("tbody").find_all("tr"):
        skill = row.get_text().split()[1]
        skills.add(skill)

    query = """INSERT INTO skill VALUES (DEFAULT, %s)
        ON CONFLICT (name) DO NOTHING;"""

    cursor.executemany(query, map(lambda skill: (skill,), skills))
    connection.commit()
    logger.info("Skills saved")

    connection.close()
    logger.info("End parse: %s", url)
