# Задание 2

Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

## threading

Идея: взять каталог книг, собрать оттуда ссылки на страницы книги, разделить url на чанки, и отдать каждому потоку.
В потоке: проходится по каждому url книги в чанке, парсит нужные данные о книге, создать pydantic модель, и отправляет запрос на бекенд из 1 лабы. (POST /books/)

```python
import threading
import requests
import time
from bs4 import BeautifulSoup
from lab_1.models.books import BookCreate

BASE_SITE_URL = "https://books.toscrape.com/"
FASTAPI_URL = "http://localhost:8000/books/"
NUM_THREADS = 10


def split_into_chunks(lst, n_chunks: int):
    length = len(lst)
    base_size = length // n_chunks
    remainder = length % n_chunks
    chunks = []
    start = 0
    for i in range(n_chunks):
        size = base_size + (1 if i < remainder else 0)
        end = start + size
        chunks.append(lst[start:end])
        start = end
    return chunks


def parse_and_save(links: list[str]):
    for link in links:
        print(f"[THREAD {threading.current_thread().name}] Start {link}")
        try:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.find("div", class_="product_main").h1.text
            desc = (
                soup.find("div", id="product_description").find_next_sibling("p").text
            )

            book = BookCreate.model_validate({"title": title, "description": desc})

            resp = requests.post(FASTAPI_URL, json=book.model_dump())
            print(
                f"[THREAD {threading.current_thread().name}] Saved '{title}'({resp.status_code})"
            )

        except Exception as e:
            print(f"[THREAD {threading.current_thread().name}] Error for {link}: {e}")


def main():
    resp = requests.get(BASE_SITE_URL + "index.html")
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.find_all("article")
    links = [BASE_SITE_URL + card.h3.a["href"] for card in cards]
    chunks = split_into_chunks(links, NUM_THREADS)
    print(f"[MAIN] Found {len(links)} books. Splitted in {len(chunks)} chunks.")

    threads = []
    start = time.time()
    for chunk in chunks:
        t = threading.Thread(target=parse_and_save, args=(chunk,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    print("[MAIN] Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    main()
```

Пример выполнения:

```
NUM_THREADS = 10

[MAIN] Found 20 books. Splitted in 10 chunks.
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
[THREAD Thread-2 (parse_and_save)] Start https://books.toscrape.com/catalogue/soumission_998/index.html       
[THREAD Thread-3 (parse_and_save)] Start https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html
[THREAD Thread-4 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html
[THREAD Thread-5 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[THREAD Thread-6 (parse_and_save)] Start https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[THREAD Thread-7 (parse_and_save)] Start https://books.toscrape.com/catalogue/set-me-free_988/index.html
[THREAD Thread-8 (parse_and_save)] Start https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html
[THREAD Thread-9 (parse_and_save)] Start https://books.toscrape.com/catalogue/olio_984/index.html
[THREAD Thread-10 (parse_and_save)] Start https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'A Light in the Attic'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
[THREAD Thread-2 (parse_and_save)] Saved 'Soumission'(200)
[THREAD Thread-2 (parse_and_save)] Start https://books.toscrape.com/catalogue/sharp-objects_997/index.html    
[THREAD Thread-3 (parse_and_save)] Saved 'Sapiens: A Brief History of Humankind'(200)
[THREAD Thread-3 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-requiem-red_995/index.html  
[THREAD Thread-8 (parse_and_save)] Saved 'Rip it Up and Start Again'(200)
[THREAD Thread-8 (parse_and_save)] Start https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[THREAD Thread-4 (parse_and_save)] Saved 'The Dirty Little Secrets of Getting Your Dream Job'(200)
[THREAD Thread-4 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[THREAD Thread-5 (parse_and_save)] Saved 'The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics'(200)
[THREAD Thread-5 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-black-maria_991/index.html  
[THREAD Thread-9 (parse_and_save)] Saved 'Olio'(200)
[THREAD Thread-9 (parse_and_save)] Start https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html
[THREAD Thread-7 (parse_and_save)] Saved 'Set Me Free'(200)
[THREAD Thread-7 (parse_and_save)] Start https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html
[THREAD Thread-6 (parse_and_save)] Saved 'Starving Hearts (Triangular Trade Trilogy, #1)'(200)
[THREAD Thread-6 (parse_and_save)] Start https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html
[THREAD Thread-10 (parse_and_save)] Saved 'Libertarianism for Beginners'(200)
[THREAD Thread-10 (parse_and_save)] Start https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Tipping the Velvet'(200)
[THREAD Thread-2 (parse_and_save)] Saved 'Sharp Objects'(200)
[THREAD Thread-3 (parse_and_save)] Saved 'The Requiem Red'(200)
[THREAD Thread-8 (parse_and_save)] Saved 'Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991'(200)
[THREAD Thread-9 (parse_and_save)] Saved 'Mesaerion: The Best Science Fiction Stories 1800-1849'(200)
[THREAD Thread-7 (parse_and_save)] Saved 'Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)'(200)
[THREAD Thread-5 (parse_and_save)] Saved 'The Black Maria'(200)
[THREAD Thread-4 (parse_and_save)] Saved 'The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull'(200)
[THREAD Thread-10 (parse_and_save)] Saved 'It's Only the Himalayas'(200)
[THREAD Thread-6 (parse_and_save)] Saved 'Shakespeare's Sonnets'(200)
[MAIN] Done in 5.575601577758789 seconds
```

```
NUM_THREADS = 1

[MAIN] Found 20 books. Splitted in 1 chunks.
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'A Light in the Attic'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Tipping the Velvet'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/soumission_998/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Soumission'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/sharp-objects_997/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Sharp Objects'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Sapiens: A Brief History of Humankind'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-requiem-red_995/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'The Requiem Red'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'The Dirty Little Secrets of Getting Your Dream Job'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/the-black-maria_991/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'The Black Maria'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Starving Hearts (Triangular Trade Trilogy, #1)'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Shakespeare's Sonnets'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/set-me-free_988/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Set Me Free'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Rip it Up and Start Again'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/olio_984/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Olio'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'Mesaerion: The Best Science Fiction Stories 1800-1849'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html      
[THREAD Thread-1 (parse_and_save)] Saved 'Libertarianism for Beginners'(200)
[THREAD Thread-1 (parse_and_save)] Start https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
[THREAD Thread-1 (parse_and_save)] Saved 'It's Only the Himalayas'(200)
[MAIN] Done in 54.654417991638184 seconds

```

## multiprocessing

В целом, идея такая же, как и в threading - делим ссылки на книги на чанки, даем каждому процессу по чанку. 

```python
from multiprocessing import Pool, current_process
import requests
import time
from bs4 import BeautifulSoup
from lab_1.models.books import BookCreate

BASE_SITE_URL = "https://books.toscrape.com/"
FASTAPI_URL = "http://localhost:8000/books/"
NUM_PROCESSES = 10


def split_into_chunks(lst, n_chunks: int):
    length = len(lst)
    base_size = length // n_chunks
    remainder = length % n_chunks
    chunks = []
    start = 0
    for i in range(n_chunks):
        size = base_size + (1 if i < remainder else 0)
        end = start + size
        chunks.append(lst[start:end])
        start = end
    return chunks


def parse_and_save(links: list[str]):
    for link in links:
        print(f"[PROCESS {current_process().name}] Start {link}")
        try:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.find("div", class_="product_main").h1.text
            desc = (
                soup.find("div", id="product_description").find_next_sibling("p").text
            )

            book = BookCreate.model_validate({"title": title, "description": desc})

            resp = requests.post(FASTAPI_URL, json=book.model_dump())
            print(
                f"[PROCESS {current_process().name}] Saved '{title}'({resp.status_code})"
            )

        except Exception as e:
            print(f"[PROCESS {current_process().name}] Error for {link}: {e}")


def main():
    resp = requests.get(BASE_SITE_URL + "index.html")
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.find_all("article")
    links = [BASE_SITE_URL + card.h3.a["href"] for card in cards]
    chunks = split_into_chunks(links, NUM_PROCESSES)
    print(f"[MAIN] Found {len(links)} books. Splitted in {len(chunks)} chunks.")

    start = time.time()
    with Pool(processes=NUM_PROCESSES) as pool:
        _ = pool.map(parse_and_save, chunks)
    print("[MAIN] Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    main()
```

```
NUM_PROCESSES = 10

[MAIN] Found 20 books. Splitted in 10 chunks.
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
[PROCESS SpawnPoolWorker-7] Start https://books.toscrape.com/catalogue/soumission_998/index.html
[PROCESS SpawnPoolWorker-6] Start https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html
[PROCESS SpawnPoolWorker-10] Start https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html
[PROCESS SpawnPoolWorker-8] Start https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[PROCESS SpawnPoolWorker-3] Start https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[PROCESS SpawnPoolWorker-5] Start https://books.toscrape.com/catalogue/set-me-free_988/index.html
[PROCESS SpawnPoolWorker-4] Start https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html
[PROCESS SpawnPoolWorker-9] Start https://books.toscrape.com/catalogue/olio_984/index.html
[PROCESS SpawnPoolWorker-2] Start https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html
[PROCESS SpawnPoolWorker-1] Saved 'A Light in the Attic'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html      
[PROCESS SpawnPoolWorker-6] Saved 'Sapiens: A Brief History of Humankind'(200)
[PROCESS SpawnPoolWorker-6] Start https://books.toscrape.com/catalogue/the-requiem-red_995/index.html
[PROCESS SpawnPoolWorker-4] Saved 'Rip it Up and Start Again'(200)
[PROCESS SpawnPoolWorker-4] Start https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[PROCESS SpawnPoolWorker-7] Saved 'Soumission'(200)
[PROCESS SpawnPoolWorker-7] Start https://books.toscrape.com/catalogue/sharp-objects_997/index.html
[PROCESS SpawnPoolWorker-10] Saved 'The Dirty Little Secrets of Getting Your Dream Job'(200)
[PROCESS SpawnPoolWorker-10] Start https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[PROCESS SpawnPoolWorker-3] Saved 'Starving Hearts (Triangular Trade Trilogy, #1)'(200)
[PROCESS SpawnPoolWorker-3] Start https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html    
[PROCESS SpawnPoolWorker-5] Saved 'Set Me Free'(200)
[PROCESS SpawnPoolWorker-5] Start https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html
[PROCESS SpawnPoolWorker-9] Saved 'Olio'(200)
[PROCESS SpawnPoolWorker-9] Start https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html
[PROCESS SpawnPoolWorker-2] Saved 'Libertarianism for Beginners'(200)
[PROCESS SpawnPoolWorker-2] Start https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html  
[PROCESS SpawnPoolWorker-8] Saved 'The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics'(200)
[PROCESS SpawnPoolWorker-8] Start https://books.toscrape.com/catalogue/the-black-maria_991/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Tipping the Velvet'(200)
[PROCESS SpawnPoolWorker-6] Saved 'The Requiem Red'(200)
[PROCESS SpawnPoolWorker-7] Saved 'Sharp Objects'(200)
[PROCESS SpawnPoolWorker-4] Saved 'Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991'(200)
[PROCESS SpawnPoolWorker-3] Saved 'Shakespeare's Sonnets'(200)
[PROCESS SpawnPoolWorker-10] Saved 'The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull'(200)
[PROCESS SpawnPoolWorker-5] Saved 'Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)'(200)
[PROCESS SpawnPoolWorker-2] Saved 'It's Only the Himalayas'(200)
[PROCESS SpawnPoolWorker-9] Saved 'Mesaerion: The Best Science Fiction Stories 1800-1849'(200)
[PROCESS SpawnPoolWorker-8] Saved 'The Black Maria'(200)
[MAIN] Done in 9.510920524597168 seconds
```

```
NUM_PROCESSES = 1

[MAIN] Found 20 books. Splitted in 1 chunks.
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
[PROCESS SpawnPoolWorker-1] Saved 'A Light in the Attic'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Tipping the Velvet'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/soumission_998/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Soumission'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/sharp-objects_997/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Sharp Objects'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html     
[PROCESS SpawnPoolWorker-1] Saved 'Sapiens: A Brief History of Humankind'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/the-requiem-red_995/index.html
[PROCESS SpawnPoolWorker-1] Saved 'The Requiem Red'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html
[PROCESS SpawnPoolWorker-1] Saved 'The Dirty Little Secrets of Getting Your Dream Job'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[PROCESS SpawnPoolWorker-1] Saved 'The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[PROCESS SpawnPoolWorker-1] Saved 'The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/the-black-maria_991/index.html
[PROCESS SpawnPoolWorker-1] Saved 'The Black Maria'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Starving Hearts (Triangular Trade Trilogy, #1)'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Shakespeare's Sonnets'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/set-me-free_988/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Set Me Free'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Rip it Up and Start Again'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/olio_984/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Olio'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Mesaerion: The Best Science Fiction Stories 1800-1849'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html
[PROCESS SpawnPoolWorker-1] Saved 'Libertarianism for Beginners'(200)
[PROCESS SpawnPoolWorker-1] Start https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
[PROCESS SpawnPoolWorker-1] Saved 'It's Only the Himalayas'(200)
[MAIN] Done in 57.774249792099 seconds
```

## asyncio

Тут я решил поэксперементировать: разделил задачи парсинга книги и задачу сохранения книги в бд, используя очередь.
Получилось, что парсеры кладут спаршенные книги (объект BookCreate) в очередь, consumer-ы берут книги из очереди и отправлят запрос на бек.

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from lab_1.models.books import BookCreate


async def parse_book(
    queue: asyncio.Queue, session: aiohttp.ClientSession, url: str
) -> BookCreate | None:
    try:
        print(f"[PARSE_BOOK] Start parsing: {url}")
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("div", class_="product_main").h1.string
            desc = (
                soup.find("div", id="product_description").find_next_sibling("p").string
            )
            new_book = BookCreate.model_validate({"title": title, "description": desc})
            await queue.put(new_book)
            print(f"[PARSE_BOOK] Parsed and added to queue: {title}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None


async def save(fastapi_session, book: BookCreate):
    print(f"[SAVE] Saving book to DB: {book.title}")
    try:
        async with fastapi_session.post("books/", json=book.model_dump()) as resp:
            print(f"[SAVE] {resp.status} Saved book: {book.title}")
    except Exception as e:
        print(f"[SAVE] Error saving {book.title}: {e}")


async def consumer(queue: asyncio.Queue, fastapi_session, consumer_id: int):
    print(f"[CONSUMER {consumer_id}] Started.")
    while True:
        book_to_save = await queue.get()
        if book_to_save:
            print(f"[CONSUMER {consumer_id}] Got book: {book_to_save.title}")
            await save(fastapi_session, book_to_save)
        queue.task_done()


async def main():
    queue = asyncio.Queue()

    start = time.time()
    async with (
        aiohttp.ClientSession(base_url="https://books.toscrape.com/") as site_session,
        aiohttp.ClientSession(base_url="http://localhost:8000/") as fastapi_session,
    ):
        print("[MAIN] Fetching main page...")
        async with site_session.get("index.html") as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            book_cards = soup.find_all("article")
            book_links = [card.h3.a["href"] for card in book_cards]

        print(f"[MAIN] Found {len(book_links)} books.")
        producer_tasks = [parse_book(queue, site_session, link) for link in book_links]

        consumer_tasks = [
            asyncio.create_task(consumer(queue, fastapi_session, i)) for i in range(10)
        ]

        await asyncio.gather(*producer_tasks)
        print("[MAIN] All books parsed and put into queue.")
        await queue.join()

        print("[MAIN] All tasks completed. Cancelling consumers...")
        for task in consumer_tasks:
            task.cancel()

        await asyncio.gather(*consumer_tasks, return_exceptions=True)
        print("[MAIN] Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    asyncio.run(main())
```

Пример выполнения:

```
[MAIN] Fetching main page...
[MAIN] Found 20 books.
[CONSUMER 0] Started.
[CONSUMER 1] Started.
[CONSUMER 2] Started.
[CONSUMER 3] Started.
[CONSUMER 4] Started.
[CONSUMER 5] Started.
[CONSUMER 6] Started.
[CONSUMER 7] Started.
[CONSUMER 8] Started.
[CONSUMER 9] Started.
[PARSE_BOOK] Start parsing: catalogue/a-light-in-the-attic_1000/index.html
[PARSE_BOOK] Start parsing: catalogue/tipping-the-velvet_999/index.html
[PARSE_BOOK] Start parsing: catalogue/soumission_998/index.html
[PARSE_BOOK] Start parsing: catalogue/sharp-objects_997/index.html
[PARSE_BOOK] Start parsing: catalogue/sapiens-a-brief-history-of-humankind_996/index.html
[PARSE_BOOK] Start parsing: catalogue/the-requiem-red_995/index.html
[PARSE_BOOK] Start parsing: catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html       
[PARSE_BOOK] Start parsing: catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[PARSE_BOOK] Start parsing: catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[PARSE_BOOK] Start parsing: catalogue/the-black-maria_991/index.html
[PARSE_BOOK] Start parsing: catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[PARSE_BOOK] Start parsing: catalogue/shakespeares-sonnets_989/index.html
[PARSE_BOOK] Start parsing: catalogue/set-me-free_988/index.html
[PARSE_BOOK] Start parsing: catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html      
[PARSE_BOOK] Start parsing: catalogue/rip-it-up-and-start-again_986/index.html
[PARSE_BOOK] Start parsing: catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[PARSE_BOOK] Start parsing: catalogue/olio_984/index.html
[PARSE_BOOK] Start parsing: catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html     
[PARSE_BOOK] Start parsing: catalogue/libertarianism-for-beginners_982/index.html
[PARSE_BOOK] Start parsing: catalogue/its-only-the-himalayas_981/index.html
[PARSE_BOOK] Parsed and added to queue: A Light in the Attic
[CONSUMER 0] Got book: A Light in the Attic
[SAVE] Saving book to DB: A Light in the Attic
[SAVE] 200 Saved book: A Light in the Attic
[PARSE_BOOK] Parsed and added to queue: The Dirty Little Secrets of Getting Your Dream Job
[CONSUMER 1] Got book: The Dirty Little Secrets of Getting Your Dream Job
[SAVE] Saving book to DB: The Dirty Little Secrets of Getting Your Dream Job
[PARSE_BOOK] Parsed and added to queue: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[PARSE_BOOK] Parsed and added to queue: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[CONSUMER 2] Got book: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[SAVE] Saving book to DB: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[CONSUMER 3] Got book: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[SAVE] Saving book to DB: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[PARSE_BOOK] Parsed and added to queue: Sapiens: A Brief History of Humankind
[PARSE_BOOK] Parsed and added to queue: Shakespeare's Sonnets
[PARSE_BOOK] Parsed and added to queue: Tipping the Velvet
[PARSE_BOOK] Parsed and added to queue: Libertarianism for Beginners
[PARSE_BOOK] Parsed and added to queue: The Black Maria
[PARSE_BOOK] Parsed and added to queue: Starving Hearts (Triangular Trade Trilogy, #1)
[PARSE_BOOK] Parsed and added to queue: Olio
[PARSE_BOOK] Parsed and added to queue: Soumission
[PARSE_BOOK] Parsed and added to queue: It's Only the Himalayas
[SAVE] 200 Saved book: The Dirty Little Secrets of Getting Your Dream Job
[CONSUMER 1] Got book: Sapiens: A Brief History of Humankind
[SAVE] Saving book to DB: Sapiens: A Brief History of Humankind
[CONSUMER 4] Got book: Shakespeare's Sonnets
[SAVE] Saving book to DB: Shakespeare's Sonnets
[CONSUMER 5] Got book: Tipping the Velvet
[SAVE] Saving book to DB: Tipping the Velvet
[CONSUMER 6] Got book: Libertarianism for Beginners
[SAVE] Saving book to DB: Libertarianism for Beginners
[CONSUMER 7] Got book: The Black Maria
[SAVE] Saving book to DB: The Black Maria
[CONSUMER 8] Got book: Starving Hearts (Triangular Trade Trilogy, #1)
[SAVE] Saving book to DB: Starving Hearts (Triangular Trade Trilogy, #1)
[CONSUMER 9] Got book: Olio
[SAVE] Saving book to DB: Olio
[CONSUMER 0] Got book: Soumission
[SAVE] Saving book to DB: Soumission
[PARSE_BOOK] Parsed and added to queue: The Requiem Red
[PARSE_BOOK] Parsed and added to queue: Mesaerion: The Best Science Fiction Stories 1800-1849
[PARSE_BOOK] Parsed and added to queue: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991
[PARSE_BOOK] Parsed and added to queue: Sharp Objects
[PARSE_BOOK] Parsed and added to queue: Set Me Free
[PARSE_BOOK] Parsed and added to queue: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[PARSE_BOOK] Parsed and added to queue: Rip it Up and Start Again
[MAIN] All books parsed and put into queue.
[SAVE] 200 Saved book: Sapiens: A Brief History of Humankind
[CONSUMER 1] Got book: It's Only the Himalayas
[SAVE] Saving book to DB: It's Only the Himalayas
[SAVE] 200 Saved book: It's Only the Himalayas
[CONSUMER 1] Got book: The Requiem Red
[SAVE] Saving book to DB: The Requiem Red
[SAVE] 200 Saved book: Soumission
[CONSUMER 0] Got book: Mesaerion: The Best Science Fiction Stories 1800-1849
[SAVE] Saving book to DB: Mesaerion: The Best Science Fiction Stories 1800-1849
[SAVE] 200 Saved book: Shakespeare's Sonnets
[CONSUMER 4] Got book: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991     
[SAVE] Saving book to DB: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991  
[SAVE] 200 Saved book: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[CONSUMER 2] Got book: Sharp Objects
[SAVE] Saving book to DB: Sharp Objects
[SAVE] 200 Saved book: Libertarianism for Beginners
[CONSUMER 6] Got book: Set Me Free
[SAVE] Saving book to DB: Set Me Free
[SAVE] 200 Saved book: Mesaerion: The Best Science Fiction Stories 1800-1849
[CONSUMER 0] Got book: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] Saving book to DB: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] 200 Saved book: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991     
[CONSUMER 4] Got book: Rip it Up and Start Again
[SAVE] Saving book to DB: Rip it Up and Start Again
[SAVE] 200 Saved book: Sharp Objects
[SAVE] 200 Saved book: Set Me Free
[SAVE] 200 Saved book: Starving Hearts (Triangular Trade Trilogy, #1)
[SAVE] 200 Saved book: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[SAVE] 200 Saved book: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] 200 Saved book: Olio
[SAVE] 200 Saved book: The Black Maria
[SAVE] 200 Saved book: Tipping the Velvet
[SAVE] 200 Saved book: The Requiem Red
[SAVE] 200 Saved book: Rip it Up and Start Again
[MAIN] All tasks completed. Cancelling consumers...
[MAIN] Done in 2.245100975036621 seconds
```

## Сравнение подходов

| Подход          | Время выполнения 1 задачи | Время выполнения 10 задач |
|-----------------|---------------------------|---------------------------|
| threading       | 54                        | 5                         |
| multiprocessing | 57                        | 9                         |
| asyncio         | -                         | 2.25                      |

Вывод: 

У нас IO-bound задача, следовательно threading и asyncio методы (как и multiprocessing) дают прирос в эффективности.

- в threading все задачи запустились как бы параллельно, но только в моменты простоя CPU (запрос на получения страницы книги, и отправка книги на бек) другие потоки так же выполнялись, что дало выигрыш по времени. 

- multiproccesing показал себя хуже, чем threading, так как процессы тяжелее потоков, и потребовалось доп. время на их обслуживание.

- в asyncio был использован другой подход, который асинхронно парсил книги и асинхронно их отправлял на бек, где другие подходы сначала парсили книгу, а потом ее отправляли (синхронно). Поэтому получилось намного быстрее.
