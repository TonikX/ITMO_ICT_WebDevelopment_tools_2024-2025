import asyncio

async def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    target = 10**9
    num_tasks = 5
    chunk_size = target // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)

    print(f"Вычисленная сумма: {total_sum}")

if __name__ == "__main__":
    asyncio.run(main())