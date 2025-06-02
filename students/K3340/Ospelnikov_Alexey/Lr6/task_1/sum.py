import time


for max_value in range(5, 10):
    t = time.time()
    cnt = 0
    for i in range(1, 10 ** max_value + 1):
        cnt += i
    
    print("Counter value:", cnt)
    print("Time:", time.time() - t)
    print("--\--\--\--\--\--\--\--\--")