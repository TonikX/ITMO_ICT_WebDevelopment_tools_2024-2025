import time, requests, psycopg2
from multiprocessing import Pool
from bs4 import BeautifulSoup

# параметры подключения к бд trip_db для пользователя postgres и пароля admin
db_parameters = {
    "dbname":   "trip_db",
    "user":     "postgres",
    "password": "admin",
    "host":     "localhost",
    "port":     5432
}

url_list = [
    "https://stackoverflow.com",
    "https://www.djangoproject.com",
    "https://realpython.com",
    "https://docs.aiohttp.org",
    "https://pypi.org"
]

k = 4

def parse_and_save(url: str) -> None:
    try:
        conn = psycopg2.connect(**db_parameters)
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pages (url, title) VALUES (%s, %s)",
                (url, title)
            )
            conn.commit()
        conn.close()
        print(f"{url} → «{title}»")
    except Exception as e:
        print(f"[multiprocessing] error for {url}: {e}")


def run_mp() -> float:
    start = time.perf_counter()
    with Pool(processes=k) as pool:
        pool.map(parse_and_save, url_list)
    return time.perf_counter() - start


if __name__ == "__main__":
    elapsed = run_mp()
    print(f"[multiprocessing] execute time: {elapsed:.3f} с")
