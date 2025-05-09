import asyncio
import time

async def partial_sum(start, end):
  return sum(range(start, end))

async def calculate_sum(n, num_tasks):
  step = n // num_tasks
  tasks = []

  for i in range(num_tasks):
    start = i * step
    end = n if i == num_tasks - 1 else (i + 1) * step
    tasks.append(asyncio.create_task(partial_sum(start, end)))

  results = await asyncio.gather(*tasks)
  return sum(results)

def main():
  n = 1_000_000_000
  num_tasks = 8
  
  start_time = time.time()

  r = asyncio.run(calculate_sum(n, num_tasks))

  end_time = time.time()

  print(f'Result: {r}')
  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Result: 499999999500000000
# Time: 17.11 seconds