import threading
import time

def compute_sum_slice(begin, finish, storage, pos):
    storage[pos] = sum(range(begin, finish))

def parallel_thread_sum():
    total_range = 1_000_000_000
    thread_count = 4
    chunk_size = total_range // thread_count
    result_parts = [0] * thread_count
    thread_pool = []

    def create_thread(i):
        left = i * chunk_size
        right = (i + 1) * chunk_size if i < thread_count - 1 else total_range
        t = threading.Thread(target=compute_sum_slice, args=(left, right, result_parts, i))
        thread_pool.append(t)
        t.start()

    for index in range(thread_count):
        create_thread(index)

    for t in thread_pool:
        t.join()

    return sum(result_parts)

if __name__ == "__main__":
    start = time.time()
    final_result = parallel_thread_sum()
    print("Final Result:", final_result)
    print("Total Time:", round(time.time() - start, 2), "seconds")
