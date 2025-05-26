import time
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import requests
from bs4 import BeautifulSoup


def get_all_books():
    book_urls = []
    current_url = URL

    while True:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        book_links = soup.select('h3 a')
        for link in book_links:
            book_url = urljoin(current_url, link['href'])
            book_urls.append(book_url)

        next_button = soup.select_one('li.next a')
        if not next_button:
            break
        current_url = urljoin(current_url, next_button['href'])

    return book_urls


def parse_and_save(book_url):
    try:
        response = requests.get(book_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("div", class_="product_main").h1.string
        description = soup.find("div", id="product_description").find_next_sibling("p").string
        api_response = requests.post(
            "http://127.0.0.1:8000/books/",
            json={
                "title": title,
                "description": description
            },
            headers={"Content-Type": "application/json"}
        )
        if api_response.status_code == 201:
            return True, title
        return False, title

    except Exception as e:
        print(f"Error processing {book_url}: {e}")
        return False, None


def worker(book_urls, results, process_id):
    for url in book_urls:
        success, title = parse_and_save(url)
        if success:
            results.append(title)
            print(f"Process {process_id}: Saved {title}")
        else:
            print(f"Process {process_id}: Failed to save {url}")


def main(count_of_processes):
    start_time = time.time()
    book_urls = get_all_books()
    size = len(book_urls) // count_of_processes
    with Manager() as manager:
        results = manager.list()
        processes = []
        for i in range(count_of_processes):
            start_idx = i * size
            end_idx = start_idx + size if i < count_of_processes - 1 else len(book_urls)
            process_urls = book_urls[start_idx:end_idx]

            process = Process(
                target=worker,
                args=(process_urls, results, i + 1)
            )
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        print(f"\nSaved {len(results)}/{len(book_urls)} books")
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")


if __name__ == '__main__':
    URL = 'https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'
    main(10)
