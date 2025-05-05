import multiprocessing

def calculate_sum(start_end):
    start, end = start_end
    return sum(range(start, end))

def main():
    target = 10**9
    num_processes = 5
    chunk_size = target // num_processes
    ranges = [(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(num_processes)]

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_sum, ranges)

    total_sum = sum(results)

    print(f"Вычисленная сумма: {total_sum}")


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()