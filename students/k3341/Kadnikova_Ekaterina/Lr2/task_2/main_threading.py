import threading
import time
import logging
from utils.scraper_utils import ScraperUtils
from utils.parser import parse_finance_page, save_category
from urls import urls
from connection import init_db
from queue import Queue
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResultStats:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.success_count = 0
        self.fail_count = 0
        self.skipped_count = 0
        self.error_types = defaultdict(int)
        self.processed_urls = []
        self.lock = threading.Lock()

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def add_success(self, url):
        with self.lock:
            self.success_count += 1
            self.processed_urls.append((url, "success"))

    def add_failure(self, url, error):
        with self.lock:
            self.fail_count += 1
            error_type = type(error).__name__
            self.error_types[error_type] += 1
            self.processed_urls.append((url, f"failed ({error_type})"))

    def add_skipped(self, url):
        with self.lock:
            self.skipped_count += 1
            self.processed_urls.append((url, "skipped"))

    def print_summary(self):
        print("\n" + "=" * 50)
        print("THREADING PARSING SUMMARY REPORT")
        print("=" * 50)
        print(f"\nTotal URLs processed: {len(self.processed_urls)}")
        print(f"Successfully processed: {self.success_count}")
        print(f"Failed: {self.fail_count}")
        print(f"Skipped: {self.skipped_count}")

        if self.error_types:
            print("\nError Types:")
            for error, count in self.error_types.items():
                print(f"- {error}: {count}")

        print("\nProcessing Details:")
        for url, status in self.processed_urls:
            print(f"- {url}: {status}")

        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            print(f"\nTotal execution time: {total_time:.2f} seconds")
            print(f"Average time per URL: {total_time / len(urls):.2f} seconds")

        print("\n" + "=" * 50)


class Worker(threading.Thread):
    def __init__(self, queue, stats):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stats = stats
        self.scraper = ScraperUtils()

    def run(self):
        while True:
            url = self.queue.get()
            if url is None:
                break

            try:
                logger.info(f"Processing: {url}")
                response = self.scraper.get_with_retry(url)

                if response and 'text/html' in response.headers.get('Content-Type', ''):
                    data = parse_finance_page(url, response.text)
                    if data:
                        save_category(data)
                        self.stats.add_success(url)
                        logger.info(f"Successfully processed: {url}")
                    else:
                        self.stats.add_skipped(url)
                        logger.warning(f"Skipped (no data): {url}")
                else:
                    self.stats.add_skipped(url)
                    logger.warning(f"Skipping non-HTML content from: {url}")

            except Exception as e:
                self.stats.add_failure(url, e)
                logger.error(f"Failed to process {url}: {str(e)}")

            self.queue.task_done()


def main():
    stats = ResultStats()
    stats.start()

    queue = Queue()

    for url in urls:
        queue.put(url)

    num_worker_threads = 3
    workers = []
    for i in range(num_worker_threads):
        worker = Worker(queue, stats)
        worker.start()
        workers.append(worker)

    queue.join()

    for i in range(num_worker_threads):
        queue.put(None)
    for worker in workers:
        worker.join()

    stats.finish()
    stats.print_summary()


if __name__ == "__main__":
    init_db()

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")