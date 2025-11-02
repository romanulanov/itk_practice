import random
import time
import json
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict


def generate_data(n: int) -> List[int]:
    return [random.randint(1, 10000) for _ in range(n)]


def process_number(number: int) -> int:
    x = number % 1000 + 500
    res = 0
    for i in range(x):
        res += i * i
    return res


def threaded(data: List[int]) -> List[int]:
    with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
        return list(executor.map(process_number, data))


def multiprocessing_pool(data: List[int]) -> List[int]:
    with mp.Pool(mp.cpu_count()) as pool:
        return pool.map(process_number, data)


def worker(input_queue: mp.Queue, output_queue: mp.Queue) -> None:
    while True:
        try:
            num = input_queue.get(timeout=2)
        except Exception:
            break
        if num is None:
            break
        try:
            result = process_number(num)
            output_queue.put(result)
        except Exception:
            output_queue.put(None)


def multiprocessing_manual(data: List[int]) -> List[int]:
    input_q = mp.Queue()
    output_q = mp.Queue()

    processes = [
        mp.Process(target=worker, args=(input_q, output_q))
        for _ in range(mp.cpu_count())
    ]

    for p in processes:
        p.start()

    for num in data:
        input_q.put(num)

    for _ in processes:
        input_q.put(None)

    results = [output_q.get() for _ in range(len(data))]

    for p in processes:
        p.join()

    return results


def benchmark(data: List[int]) -> Dict[str, float]:
    variants = [
        ("ThreadPoolExecutor", threaded),
        ("Multiprocessing.Pool", multiprocessing_pool),
        ("Manual multiprocessing", multiprocessing_manual),
    ]

    results_summary = {}

    for name, func in variants:
        start = time.perf_counter()
        _ = func(data)
        elapsed = time.perf_counter() - start

        print(f"{name:<25} | {elapsed:.2f} сек")
        results_summary[name] = elapsed

    return results_summary


def benchmark_series():
    sizes = [10000, 100000, 1000000]
    all_results = {}

    for n in sizes:
        print(f"\n=== Тест для n={n:,} ===")
        data = generate_data(n)
        res = benchmark(data)
        all_results[n] = res

    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    return all_results


if __name__ == "__main__":
    all_results = benchmark_series()
