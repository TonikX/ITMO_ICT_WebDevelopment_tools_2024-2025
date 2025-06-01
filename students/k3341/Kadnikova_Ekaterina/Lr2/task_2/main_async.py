import asyncio
import logging
from utils.async_utils import AsyncScraper
from utils.async_parser import parse_finance_page, save_category_async
from urls import urls
from utils.async_connection import init_db
import time
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

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    def add_success(self, url):
        self.success_count += 1
        self.processed_urls.append((url, "success"))

    def add_failure(self, url, error):
        self.fail_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] += 1
        self.processed_urls.append((url, f"failed ({error_type})"))

    def add_skipped(self, url):
        self.skipped_count += 1
        self.processed_urls.append((url, "skipped"))

    def print_summary(self):
        print("\n" + "=" * 50)
        print("ASYNC PARSING SUMMARY REPORT")
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

        if self.start_time and self.end_time and len(self.processed_urls):
            total_time = self.end_time - self.start_time
            avg_time = total_time / len(self.processed_urls)
            print(f"\nTotal execution time: {total_time:.2f} seconds")
            print(f"Average time per URL: {avg_time:.2f} seconds")

        print("\n" + "=" * 50)


async def process_url(scraper: AsyncScraper, session, url: str, stats: ResultStats):
    try:
        logger.info(f"Processing: {url}")
        html = await scraper.get_with_retry(session, url)

        if not html:
            stats.add_skipped(url)
            logger.warning(f"Skipped (no HTML): {url}")
            return

        data = parse_finance_page(url, html)
        if not data:
            stats.add_skipped(url)
            logger.warning(f"Skipped (no data): {url}")
            return

        await save_category_async(data)
        stats.add_success(url)
        logger.info(f"Successfully processed: {url}")

    except Exception as e:
        stats.add_failure(url, e)
        logger.error(f"Failed to process {url}: {str(e)}")


async def main():
    stats = ResultStats()
    stats.start()
    scraper = AsyncScraper()

    try:
        async with await scraper.create_session() as session:
            tasks = [
                asyncio.create_task(process_url(scraper, session, url, stats))
                for url in urls
            ]
            await asyncio.gather(*tasks, return_exceptions=False)

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")

    finally:
        await scraper.close()
        stats.finish()
        stats.print_summary()


if __name__ == "__main__":
    asyncio.run(init_db())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
