import multiprocessing
import time
from parser import parse_and_save

def process_url(url):
    parse_and_save(url, table_name="specializations_multiprocessing")

def main():
    with open('specialization_urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    start_time = time.time()

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_url, urls)

    end_time = time.time()

    print(f"Multiprocessing finished in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
