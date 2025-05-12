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


"""

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

"""
