import asyncio
import threading_, async_, multiprocessing_


def main():
    print("\nThreading:")
    threading_.main()

    print("\nMultiprocessing:")
    multiprocessing_.main()

    print("\nAsync:")
    asyncio.run(async_.main())


if __name__ == "__main__":
    main()
