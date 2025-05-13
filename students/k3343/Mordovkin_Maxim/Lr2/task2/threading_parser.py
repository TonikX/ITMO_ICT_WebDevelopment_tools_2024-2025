import time, threading, requests
from bs4 import BeautifulSoup
from psycopg2.pool import ThreadedConnectionPool


k = 4

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


def parse_and_save(url: str, pool: ThreadedConnectionPool) -> None:
    conn = pool.getconn()
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pages (url, title) VALUES (%s, %s)",
                (url, title)
            )
            conn.commit()
        print(f"{url} → «{title}»")
    except Exception as e:
        print(f"[threading] error for {url}: {e}")
    finally:
        pool.putconn(conn)


def run_thread() -> float:
    pool = ThreadedConnectionPool(1, k, **db_parameters)

    g, m = divmod(len(url_list), k)
    parts = [
        url_list[i*g + min(i, m):(i+1)*g + min(i+1, m)]
        for i in range(k)
    ]

    threads = []
    start = time.perf_counter()
    for part in parts:
        t = threading.Thread(
            target=lambda lst: [parse_and_save(u, pool) for u in lst],
            args=(part,)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    pool.closeall()
    return time.perf_counter() - start


if __name__ == "__main__":
    elapsed = run_thread()
    print(f"[threading] execute time: {elapsed:.3f} с")
