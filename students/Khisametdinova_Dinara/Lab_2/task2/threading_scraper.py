import threading
import time
from parser import parse_and_save

def main():
    with open('specialization_urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    threads = []

    start_time = time.time()

    for url in urls:
        t = threading.Thread(target=parse_and_save, args=(url, "specializations_threading"))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    print(f"Threading finished in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
