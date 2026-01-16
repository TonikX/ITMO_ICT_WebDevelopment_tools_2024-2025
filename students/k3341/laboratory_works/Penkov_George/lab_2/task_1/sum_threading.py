import threading
import time


result = 0


def calculate_sum(start: int, end: int):
    global result
    subsum = 0
    print(f"{threading.current_thread().name} started summing from {start} to {end}")
    for i in range(start, end + 1):
        subsum += i
    print(f"{threading.current_thread().name} finished. subsum={subsum}")
    result += subsum


if __name__ == "__main__":
    NUM_THREADS = 10
    START = 1
    END = 10**9

    threads = []
    cur_start = 1
    step = END // NUM_THREADS
    cur_end = cur_start + step - 1

    start = time.time()
    for i in range(NUM_THREADS):
        t = threading.Thread(target=calculate_sum, args=(cur_start, cur_end))
        threads.append(t)
        t.start()
        cur_start = cur_end + 1
        cur_end = cur_start + step - 1

    for t in threads:
        t.join()

    print("Final sum=", result)
    print("Done in", time.time() - start, "seconds")

"""
NUM_THREADS = 10

Thread-1 (calculate_sum) started summing from 1 to 100000000
Thread-2 (calculate_sum) started summing from 100000001 to 200000000
Thread-3 (calculate_sum) started summing from 200000001 to 300000000
Thread-4 (calculate_sum) started summing from 300000001 to 400000000
Thread-5 (calculate_sum) started summing from 400000001 to 500000000
Thread-6 (calculate_sum) started summing from 500000001 to 600000000
Thread-7 (calculate_sum) started summing from 600000001 to 700000000
Thread-8 (calculate_sum) started summing from 700000001 to 800000000
Thread-9 (calculate_sum) started summing from 800000001 to 900000000
Thread-10 (calculate_sum) started summing from 900000001 to 1000000000
Thread-4 (calculate_sum) finished. subsum=35000000050000000
Thread-6 (calculate_sum) finished. subsum=55000000050000000
Thread-2 (calculate_sum) finished. subsum=15000000050000000
Thread-1 (calculate_sum) finished. subsum=5000000050000000
Thread-9 (calculate_sum) finished. subsum=85000000050000000
Thread-7 (calculate_sum) finished. subsum=65000000050000000
Thread-10 (calculate_sum) finished. subsum=95000000050000000
Thread-8 (calculate_sum) finished. subsum=75000000050000000
Thread-5 (calculate_sum) finished. subsum=45000000050000000
Thread-3 (calculate_sum) finished. subsum=25000000050000000
Final sum= 500000000500000000
Done in 39.592371463775635 seconds
"""

"""
NUM_THREADS = 1

Thread-1 (calculate_sum) started summing from 1 to 1000000000
Thread-1 (calculate_sum) finished. subsum=500000000500000000
Final sum= 500000000500000000
Done in 40.29339575767517 seconds
"""
