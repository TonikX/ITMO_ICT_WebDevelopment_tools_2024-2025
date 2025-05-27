from multiprocessing import Process, Manager
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))

def main():
    total = 1000_000_000
    processes_num = 4
    chunk_size = total // processes_num

    with Manager() as manager:
        results = manager.list([0] * processes_num)
        processes = []

        start_time = time.time()

        for i in range(processes_num):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size if i != processes_num - 1 else total
            process = Process(
                target=calculate_sum,
                args=(start, end, results, i))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        total_sum = sum(results)
        end_time = time.time()

    print(f"Multiprocessing sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()