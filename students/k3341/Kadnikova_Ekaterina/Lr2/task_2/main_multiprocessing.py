import multiprocessing
import time
import requests
from utils.parser import parse_finance_page, save_category
from urls import urls
from connection import init_db
from fake_useragent import UserAgent
import logging
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResultStats:
    def __init__(self, manager):
        self.success_count = manager.Value('i', 0)
        self.fail_count = manager.Value('i', 0)
        self.skipped_count = manager.Value('i', 0)
        self.error_types = manager.dict()
        self.processed_urls = manager.list()
        self.lock = manager.Lock()
        self.start_time = time.time()

    def update_stats(self, url, status, error_type=None):
        with self.lock:
            if status == "success":
                self.success_count.value += 1
                self.processed_urls.append((url, "success"))
            elif status == "skipped":
                self.skipped_count.value += 1
                self.processed_urls.append((url, "skipped"))
            elif status == "failed":
                self.fail_count.value += 1
                if error_type:
                    self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
                self.processed_urls.append((url, f"failed ({error_type})"))

    def print_summary(self):
        total_time = time.time() - self.start_time
        print("\n" + "=" * 50)
        print("MULTIPROCESSING PARSING SUMMARY REPORT")
        print("=" * 50)

        total_processed = (self.success_count.value +
                           self.fail_count.value +
                           self.skipped_count.value)

        print(f"\nTotal URLs processed: {total_processed}")
        print(f"Successfully processed: {self.success_count.value}")
        print(f"Failed: {self.fail_count.value}")
        print(f"Skipped: {self.skipped_count.value}")

        if self.error_types:
            print("\nError Types:")
            for error, count in self.error_types.items():
                print(f"- {error}: {count}")

        print("\nProcessing Details:")
        for url, status in self.processed_urls:
            print(f"- {url}: {status}")

        print(f"\nTotal execution time: {total_time:.2f} seconds")
        if total_processed > 0:
            print(f"Average time per URL: {total_time / total_processed:.2f} seconds")
        print("\n" + "=" * 50)


def get_session():
    session = requests.Session()
    ua = UserAgent()
    session.headers.update({
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1'
    })
    return session


def process_url(url, stats):
    session = get_session()
    try:
        logger.info(f"Processing: {url}")

        try:
            try:
                hostname = url.split('/')[2]
                socket.gethostbyname(hostname)
            except socket.gaierror as e:
                logger.error(f"DNS resolution failed for {url}: {str(e)}")
                stats.update_stats(url, "failed", "DNSResolutionError")
                return

            response = session.get(url, timeout=15)

            if response.status_code == 403:
                session.headers.update({
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                })
                response = session.get(url, timeout=15)

            response.raise_for_status()

            if 'text/html' in response.headers.get('Content-Type', ''):
                data = parse_finance_page(url, response.text)
                if data:
                    save_category(data)
                    stats.update_stats(url, "success")
                    logger.info(f"Successfully processed: {url}")
                else:
                    stats.update_stats(url, "skipped")
                    logger.warning(f"Skipped (no data): {url}")
            else:
                stats.update_stats(url, "skipped")
                logger.warning(f"Skipping non-HTML content from: {url}")

        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            stats.update_stats(url, "failed", error_type)
            logger.error(f"Request error for {url}: {str(e)}")

    except Exception as e:
        error_type = type(e).__name__
        stats.update_stats(url, "failed", error_type)
        logger.error(f"Unexpected error processing {url}: {str(e)}")


def worker(url_queue, stats):
    while True:
        url = url_queue.get()
        if url is None:
            break
        process_url(url, stats)
        url_queue.task_done()


def main():
    init_db()
    manager = multiprocessing.Manager()
    stats = ResultStats(manager)

    url_queue = multiprocessing.JoinableQueue()

    for url in urls:
        url_queue.put(url)

    num_processes = min(3, len(urls))
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=worker, args=(url_queue, stats))
        p.start()
        processes.append(p)

    url_queue.join()

    for i in range(num_processes):
        url_queue.put(None)
    for p in processes:
        p.join()

    stats.print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")