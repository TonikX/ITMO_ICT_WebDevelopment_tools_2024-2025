import multiprocessing
import time

def calculate_partial_sum(start, end):
    return sum(range(start, end))

def main():
    start_time = time.time()
    n_processes = 5
    total = 1000000000
    chunk_size = total // n_processes
    pool = multiprocessing.Pool(processes=n_processes)
    tasks = [(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(n_processes)]

    results = pool.starmap(calculate_partial_sum, tasks)
    pool.close()
    pool.join()

    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 21.549757957458496

if __name__ == "__main__":
    main()
