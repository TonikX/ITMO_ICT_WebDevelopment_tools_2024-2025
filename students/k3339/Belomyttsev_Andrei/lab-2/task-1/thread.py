import threading
import time

def partial_sum(start, end, r, i):
  r[i] = (sum(range(start, end)))

def calculate_sum(n, num_tasks):
  step = n // num_tasks
  r = [0] * num_tasks
  tasks = []

  for i in range(num_tasks):
    start = i * step
    end = n if i == num_tasks - 1 else (i + 1) * step
    task = threading.Thread(target=partial_sum, args=(start, end, r, i))
    tasks.append(task)
    task.start()
  
  for task in tasks:
    task.join()

  return sum(r)

def main():
  n = 1_000_000_000
  num_tasks = 8
  
  start_time = time.time()

  r = calculate_sum(n, num_tasks)

  end_time = time.time()

  print(f'Result: {r}')
  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Result: 499999999500000000
# Time: 16.87 seconds