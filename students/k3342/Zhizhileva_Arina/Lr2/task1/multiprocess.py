import time
from multiprocessing import Pool, freeze_support

def sum_segment(start_idx, end_idx):
    return sum(range(start_idx, end_idx))

def run_parallel_sum():
    total_items = 1_000_000_000
    workers = 4
    chunk = total_items // workers

    boundaries = [
        (i * chunk, (i + 1) * chunk if i < workers - 1 else total_items)
        for i in range(workers)
    ]

    with Pool(processes=workers) as pool:
        partial_results = pool.starmap(sum_segment, boundaries)

    return sum(partial_results)

def main():
    freeze_support()  # For Windows compatibility
    t0 = time.time()
    total = run_parallel_sum()
    print("Total Sum:", total)
    print("Elapsed Time:", round(time.time() - t0, 2), "seconds")

if __name__ == "__main__":
    main()
