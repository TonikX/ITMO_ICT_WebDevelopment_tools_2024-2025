import multiprocessing
import time

def partial_sum(start, end):
  return sum(range(start, end))

def calculate_sum(n, num_tasks):
  step = n // num_tasks
  ranges = []

  for i in range(num_tasks):
    start = i * step
    end = n if i == num_tasks - 1 else (i + 1) * step
    ranges.append((start, end))

  with multiprocessing.Pool(processes=num_tasks) as pool:
    r = pool.starmap(partial_sum, ranges)

  return sum(r)

def main():
  n = 1_000_000_000
  num_tasks = 8
  # print(multiprocessing.cpu_count()) # 8
  
  start_time = time.time()

  r = calculate_sum(n, num_tasks)

  end_time = time.time()

  print(f'Result: {r}')
  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Result: 499999999500000000
# Time: 4.80 seconds