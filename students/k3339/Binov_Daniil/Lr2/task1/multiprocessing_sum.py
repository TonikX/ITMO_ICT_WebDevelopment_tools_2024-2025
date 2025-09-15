import time
from multiprocessing import Process, Manager

def calculate_partial_sum(start, end):
    return end * (end + 1) // 2 - (start - 1) * start // 2

def target(idx, s, e, results):
    results[idx] = calculate_partial_sum(s, e)

if __name__ == '__main__':
    N = 10000000000000  
    NUM_PROCESSES = 4   
    chunk_size = N // NUM_PROCESSES  

    start_time = time.time()

    manager = Manager()
    results = manager.list([0] * NUM_PROCESSES)

    processes = []
    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_PROCESSES - 1 else N
        process = Process(target=target, args=(i, start, end, results))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    total_sum = sum(results)

    end_time = time.time()
    print(f"Multiprocessing sum: {total_sum}")
    print(f"Multiprocessing time: {end_time - start_time} seconds")