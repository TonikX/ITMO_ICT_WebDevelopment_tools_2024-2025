import threading
import time

def calculate_sum(start, end, result, index):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result[index] = partial_sum

def main():
    n = 10**8
    num_threads = 4
    chunk_size = n // num_threads
    result = [0] * num_threads
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else n
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_sum = sum(result)
    end_time = time.time()
    
    print(f"Threading result: {total_sum}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()