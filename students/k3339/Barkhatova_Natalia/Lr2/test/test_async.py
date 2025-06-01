import asyncio
import time

N = 10_000_000
NUM_TASKS = 4
results = [0] * NUM_TASKS


async def calculate_sum(start, end, index):
    results[index] = sum(range(start, end))


async def main():
    chunk_size = N // NUM_TASKS
    tasks = []

    for i in range(NUM_TASKS):
        start = i * chunk_size
        end = N if i == NUM_TASKS - 1 else (i + 1) * chunk_size
        tasks.append(calculate_sum(start, end, i))

    await asyncio.gather(*tasks)
    total = sum(results)
    print(f"Сумма: {total}")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Затрачено времени: {end - start:.2f} секунд")
