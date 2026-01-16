import asyncio
import time


async def calculate_sum(start: int, end: int):
    subsum = 0
    print(f"Started summing from {start} to {end}")
    for i in range(start, end + 1):
        subsum += i
    print(f"Finished summing from {start} to {end}. subsum={subsum}")
    return subsum


async def main():
    NUM_CORUTINES = 10
    START = 1
    END = 10**9

    step = END // NUM_CORUTINES
    cur_start = START
    cur_end = cur_start + step - 1

    tasks = []

    start = time.time()
    for i in range(NUM_CORUTINES):
        tasks.append(asyncio.create_task(calculate_sum(cur_start, cur_end)))
        cur_start = cur_end + 1
        cur_end = cur_start + step - 1
    subsums = await asyncio.gather(*tasks)
    fullsum = sum(subsums)
    print("Final sum=", fullsum)
    print("Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    asyncio.run(main())


"""
NUM_CORUTINES = 5

Started summing from 1 to 200000000
Finished summing from 1 to 200000000. subsum=20000000100000000
Started summing from 200000001 to 400000000
Finished summing from 200000001 to 400000000. subsum=60000000100000000
Started summing from 400000001 to 600000000
Finished summing from 400000001 to 600000000. subsum=100000000100000000
Started summing from 600000001 to 800000000
Finished summing from 600000001 to 800000000. subsum=140000000100000000
Started summing from 800000001 to 1000000000
Finished summing from 800000001 to 1000000000. subsum=180000000100000000
Final sum= 500000000500000000
Done in 40.858588457107544 seconds
"""

"""
NUM_CORUTINES = 1

Started summing from 1 to 1000000000
Finished summing from 1 to 1000000000. subsum=500000000500000000
Final sum= 500000000500000000
Done in 41.3083233833313 seconds
"""
