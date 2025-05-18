import threading
import requests
import certifi
import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, Session, create_engine
from models.models import Preference

load_dotenv()

DATABASE_URL = os.getenv("DB_ADMIN")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

def parse_and_save(url: str):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, "html.parser")
        name = url.split("/")[-1].capitalize()

        with Session(engine) as db:
            pref = Preference(name=name)
            db.add(pref)
            db.commit()
            print(f"[OK] Saved preference: {name}")
        return {"status": "ok", "name": name}
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return {"status": "error", "error": str(e)}

def run_parser(urls: list[str]):
    start = time.time()
    threads = []
    results = []

    def worker(url):
        result = parse_and_save(url)
        results.append(result)

    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    duration = round(time.time() - start, 2)
    return {"results": results, "time": duration}