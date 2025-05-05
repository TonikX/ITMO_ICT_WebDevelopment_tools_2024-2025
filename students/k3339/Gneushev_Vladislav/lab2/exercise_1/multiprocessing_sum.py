import multiprocessing
import time


def calculate_sum(start, end):
    local_sum = 0
    for i in range(start, end + 1):
        local_sum += i
    return local_sum


if __name__ == "__main__":
    TOTAL_SUM_UP_TO = 100_000_000 
    NUM_PROCESSES = 4
    total_sum = 0
    
    chunk_size = TOTAL_SUM_UP_TO // NUM_PROCESSES
    tasks = []
    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_PROCESSES - 1 else TOTAL_SUM_UP_TO
        tasks.append((start, end))

    start_time = time.perf_counter()
    
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        partial_sums = pool.starmap(calculate_sum, tasks)

    total_sum = sum(partial_sums)
    end_time = time.perf_counter()

    print(f"Multiprocessing")
    print(f"Calculated sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")