import asyncio
import time
import logging
from sum.threading_sum import calculate_sum as threading_calculate_sum
from sum.multiprocessing_sum import calculate_sum as multiprocessing_calculate_sum
from sum.async_sum import calculate_sum as async_calculate_sum
from parsers.threading_parser import parse_urls as threading_parse_urls
from parsers.multiprocessing_parser import parse_urls as multiprocessing_parse_urls
from parsers.async_parser import parse_pages as async_parse_urls
from utils.sum_logger import log_sum_operation, log_sum_operation_async
from utils.parser_logger import log_parser_operation, log_parser_operation_async

TARGET_POWER = 8
NUM_WORKERS = 10

TEST_URLS = [
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com",
    "https://www.wikipedia.org"
]

async def run_async_tests():
    print("\nasync tests...")
    await log_sum_operation_async("async", async_calculate_sum, TARGET_POWER, NUM_WORKERS)
    print("Running async parser...")
    await log_parser_operation_async("async", async_parse_urls, TEST_URLS)

def main():
    print("target power:", TARGET_POWER)
    print("num workers:", NUM_WORKERS)
    print("\nStarting tests...")
    
    asyncio.run(run_async_tests())
    
    print("\nthreading tests...")
    log_sum_operation("threading", threading_calculate_sum, TARGET_POWER, NUM_WORKERS)
    log_parser_operation("threading", threading_parse_urls, TEST_URLS)
    
    print("\nmultiprocessing tests...")
    log_sum_operation("multiprocessing", multiprocessing_calculate_sum, TARGET_POWER, NUM_WORKERS)
    log_parser_operation("multiprocessing", multiprocessing_parse_urls, TEST_URLS)

if __name__ == "__main__":
    main() 