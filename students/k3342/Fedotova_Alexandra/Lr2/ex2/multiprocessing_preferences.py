from multiprocessing import Process
import requests
import certifi
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, Session, create_engine
from models import Preference
import time

load_dotenv()

DATABASE_URL = os.getenv("DB_ADMIN")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

urls = [
    "https://www.tourradar.com/i/beach",
    "https://www.tourradar.com/i/culture",
    "https://www.tourradar.com/i/adventure",
    "https://www.tourradar.com/i/trekking",
    "https://www.tourradar.com/i/wildlife",
    "https://www.tourradar.com/i/sightseeing"
]

def parse_and_save(url):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, "html.parser")
        name = url.split("/")[-1].capitalize()

        with Session(engine) as db:
            pref = Preference(name=name)
            db.add(pref)
            db.commit()
            print(f"[OK] Saved preference: {name}")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")

if __name__ == "__main__":
    start = time.time()
    processes = []
    for url in urls:
        p = Process(target=parse_and_save, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    print(f"Finished in {time.time() - start:.2f} seconds")
