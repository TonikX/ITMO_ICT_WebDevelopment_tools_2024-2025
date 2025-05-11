import time, threading, multiprocessing as mp, asyncio
import matplotlib.pyplot as plt


def _chunk_bounds(start: int, end: int, chunks: int):
    length = end - start + 1
    step, extra = divmod(length, chunks)
    bounds, current = [], start
    for i in range(chunks):
        size = step + (1 if i < extra else 0)
        bounds.append((current, current + size - 1))
        current += size
    return bounds


def _sum_range(a: int, b: int):
    s = 0
    for x in range(a, b + 1):
        s += x
    return s


def _sum_threading(n: int, workers: int):
    bounds = _chunk_bounds(1, n, workers)
    partial = [0] * workers

    def worker(idx: int, seg):
        partial[idx] = _sum_range(*seg)

    threads = [threading.Thread(target=worker, args=(i, seg)) for i, seg in enumerate(bounds)]
    t0 = time.perf_counter()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return sum(partial), time.perf_counter() - t0


def _mp_worker(seg, q):
    q.put(_sum_range(*seg))


def _sum_multiprocessing(n: int, workers: int):
    bounds = _chunk_bounds(1, n, workers)
    ctx = mp.get_context("fork" if hasattr(mp, "get_context") else None)
    q = ctx.Queue()
    procs = [ctx.Process(target=_mp_worker, args=(seg, q)) for seg in bounds]
    t0 = time.perf_counter()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return sum(q.get() for _ in bounds), time.perf_counter() - t0


async def _async_main(n: int, workers: int):
    bounds = _chunk_bounds(1, n, workers)
    loop = asyncio.get_running_loop()
    t0 = time.perf_counter()
    tasks = [loop.run_in_executor(None, _sum_range, seg[0], seg[1]) for seg in bounds]
    partials = await asyncio.gather(*tasks)
    return sum(partials), time.perf_counter() - t0


def _sum_asyncio(n: int, workers: int):
    return asyncio.run(_async_main(n, workers))


def _plot(times: dict):
    plt.figure(figsize=(8, 5))
    plt.bar(times.keys(), times.values())
    plt.ylabel("Seconds")
    plt.title("Naive sum 1..10**10 (lower is better)")
    plt.savefig("benchmark_results.png", bbox_inches="tight")
    plt.close()


def main():
    N = 10 ** 10
    workers = mp.cpu_count()
    ref = N * (N + 1) // 2
    results = {}

    total, t = _sum_threading(N, workers)
    assert total == ref
    results["threading"] = t

    total, t = _sum_multiprocessing(N, workers)
    assert total == ref
    results["multiprocessing"] = t

    total, t = _sum_asyncio(N, workers)
    assert total == ref
    results["asyncio"] = t

    _plot(results)
    for k, v in results.items():
        print(f"{k}: {v:.2f}s")


if __name__ == "__main__":
    main()
