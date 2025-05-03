import multiprocessing
import time
from concurrent.futures import Future, ProcessPoolExecutor


def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


def main() -> None:
    start_time = time.perf_counter()
    with ProcessPoolExecutor(max_workers=MAX_CONCURENCY) as executor:
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


# import multiprocessing
# import time


# def calculate_sum(start: int, end: int, shared: list[int]) -> None:
#     shared.append(sum(num for num in range(start + 1, end + 1)))


# N = 100_000_000
# MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
# N_per_process = N // MAX_CONCURENCY


# def main() -> None:
#     manager = multiprocessing.Manager()
#     shared = manager.list()
#     processes: list[multiprocessing.Process] = []

#     start_time = time.perf_counter()
#     for offset in range(MAX_CONCURENCY):
#         start = offset * N_per_process
#         end = offset * N_per_process + N_per_process
#         process = multiprocessing.Process(
#             target=calculate_sum, args=(start, end, shared)
#         )

#         processes.append(process)
#         process.start()

#     for process in processes:
#         process.join()

#     print(f"Результат: {sum(shared)}")
#     print(f"Время: {time.perf_counter() - start_time}")


# if __name__ == "__main__":
#     main()
