import logging
import os
from concurrent.futures import ThreadPoolExecutor

import psycopg2
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_and_save(url: str) -> None:
    connection = psycopg2.connect(os.getenv("POSTGRES_URL"))
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


def main(urls: list[str]) -> None:
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(parse_and_save, urls)
