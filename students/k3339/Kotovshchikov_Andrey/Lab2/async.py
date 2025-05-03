import asyncio
import multiprocessing
import time


async def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


async def main() -> None:
    start_time = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tasks: list[asyncio.Task[int]] = []
        for offset in range(MAX_CONCURENCY):
            task = tg.create_task(
                calculate_sum(
                    start=offset * N_per_process,
                    end=offset * N_per_process + N_per_process,
                ),
            )

            tasks.append(task)

    print(f"Результат: {sum([task.result() for task in tasks])}")
    print(f"Время: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    asyncio.run(main())
