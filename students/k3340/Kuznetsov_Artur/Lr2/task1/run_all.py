import asyncio
import threading_sum, async_sum, multiprocessing_sum


def main():
    print("\nThreading:")
    threading_sum.main()

    print("\nMultiprocessing:")
    multiprocessing_sum.main()

    print("\nAsync:")
    asyncio.run(async_sum.main())


if __name__ == "__main__":
    main()
