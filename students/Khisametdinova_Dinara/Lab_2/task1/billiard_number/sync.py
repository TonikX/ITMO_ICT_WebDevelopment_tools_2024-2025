import time

def compute_segment_sum(start_value, end_value):
    return sum(range(start_value, end_value + 1))

def run_sync_sum(total_limit=10**9, segments=4):
    t0 = time.time()

    size = total_limit // segments
    boundaries = [
        (i * size + 1, (i + 1) * size if i < segments - 1 else total_limit)
        for i in range(segments)
    ]

    segment_results = [compute_segment_sum(a, b) for a, b in boundaries]
    total_sum = sum(segment_results)

    t1 = time.time()
    print(f"Sum: {total_sum}")
    print(f"Time: {t1 - t0:.2f} seconds")

if __name__ == "__main__":
    run_sync_sum()
