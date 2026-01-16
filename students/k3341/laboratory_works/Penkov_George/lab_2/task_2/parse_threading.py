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


"""
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
"""
