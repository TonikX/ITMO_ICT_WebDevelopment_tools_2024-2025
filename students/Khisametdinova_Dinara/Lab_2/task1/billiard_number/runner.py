import asyncio
import threading_sum
import multiprocessing_sum
import async_sum
import sync

def main():

    print("\nSync")
    sync.run_sync_sum()

    print("\nThreading:")
    threading_sum.main()

    print("\nMultiprocessing:")
    multiprocessing_sum.main()

    print("\nAsync:")
    asyncio.run(async_sum.run_async_sum())

if __name__ == "__main__":
    main()
