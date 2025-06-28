import multiprocessing
import time

def calculate_sum(start, end, result, index):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result[index] = partial_sum  

def main():
    n = 10**8  
    num_processes = 4
    chunk_size = n // num_processes
    result = multiprocessing.Array('q', num_processes)  
    
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_processes - 1 else n
        process = multiprocessing.Process(
            target=calculate_sum,
            args=(start, end, result, i)
        )
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    total_sum = sum(result)
    end_time = time.time()
    
    print(f"Multiprocessing result: {total_sum}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()