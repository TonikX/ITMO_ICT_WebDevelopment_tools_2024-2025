import multiprocessing
import time
from concurrent.futures import Future, ThreadPoolExecutor


def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


def main() -> None:
    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=MAX_CONCURENCY) as executor:
        futures: list[Future[int]] = []
        for offset in range(MAX_CONCURENCY):
            future = executor.submit(
                calculate_sum,
                start=offset * N_per_process,
                end=offset * N_per_process + N_per_process,
            )

            futures.append(future)

    print(f"Результат: {sum([future.result() for future in futures])}")
    print(f"Время: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    main()


# import threading
# import multiprocessing
# import time


# def calculate_sum(start: int, end: int, shared: list[int]) -> None:
#     shared.append(sum(num for num in range(start + 1, end + 1)))


# N = 100_000_000
# MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
# N_per_thread = N // MAX_CONCURENCY


# def main() -> None:
#     shared = []
#     threads: list[threading.Thread] = []

#     start_time = time.perf_counter()
#     for offset in range(MAX_CONCURENCY):
#         start = offset * N_per_thread
#         end = offset * N_per_thread + N_per_thread
#         thread = threading.Thread(target=calculate_sum, args=(start, end, shared))

#         threads.append(thread)
#         thread.start()

#     for thread in threads:
#         thread.join()

#     print(f"Результат: {sum(shared)}")
#     print(f"Время: {time.perf_counter() - start_time}")


# if __name__ == "__main__":
#     main()
