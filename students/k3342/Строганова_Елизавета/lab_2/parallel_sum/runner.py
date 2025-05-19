
import time
import asyncio
from .multiprocessing_sum import multiprocess_sum
from .threading_sum import threaded_sum
from .thread_executor import threadpool_sum

def run_and_measure(label: str, func, *args):
    print(f"\n⏱ Running: {label}")
    start = time.time()
    result = func(*args) if not asyncio.iscoroutinefunction(func) else asyncio.run(func(*args))
    duration = round(time.time() - start, 2)
    print(f"{label} Result: {result}")
    print(f"{label} Time: {duration} seconds")
    return result

def main():
    total = 1_000_000_000
    workers = 4

    run_and_measure("Multiprocessing", multiprocess_sum, total, workers)
    run_and_measure("Threading", threaded_sum, total, workers)
    run_and_measure("ThreadPoolExecutor + asyncio", threadpool_sum, total, workers)

if __name__ == "__main__":
    main()
