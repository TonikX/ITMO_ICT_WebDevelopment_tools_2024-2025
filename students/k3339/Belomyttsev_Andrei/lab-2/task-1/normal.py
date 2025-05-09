import time

def main():
  n = 1_000_000_000

  start_time = time.time()

  r = sum(range(0, n))

  end_time = time.time()

  print(f'Result: {r}')
  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Result: 499999999500000000
# Time: 16.57 seconds