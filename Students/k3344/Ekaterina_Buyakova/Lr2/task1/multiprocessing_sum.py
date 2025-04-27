import multiprocessing
import time

def sum_in_range(start, end, return_dict, idx):
    total = 0
    for n in range(start, end):
        total += n
    return_dict[idx] = total

def calculate_sum(limit, num_processes):
    print(f"Считаем сумму от 1 до {limit} используя {num_processes} процессов...")

    start_time = time.time()

    manager = multiprocessing.Manager()
    results = manager.dict()
    jobs = []

    part = limit // num_processes
    sections = [
        (i * part + 1, (i + 1) * part + 1 if i < num_processes - 1 else limit + 1)
        for i in range(num_processes)
    ]

    for idx, (begin, finish) in enumerate(sections):
        proc = multiprocessing.Process(target=sum_in_range, args=(begin, finish, results, idx))
        jobs.append(proc)
        proc.start()

    for proc in jobs:
        proc.join()

    total_sum = sum(results.values())
    end_time = time.time()

    print(f"Итоговая сумма: {total_sum}")
    print(f"Процессы: {num_processes}")
    print(f"Затраченное время: {end_time - start_time:.3f} сек")

if __name__ == "__main__":
    border_value = 1000000000
    for proc_count in range(4, 5):
        calculate_sum(border_value, proc_count)
