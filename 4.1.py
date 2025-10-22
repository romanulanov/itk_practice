import random
import math
import time
import json
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp


def generate_data(n: int):
    return [random.randint(1, 10000) for _ in range(n)]


def process_number(number: int):
    return math.factorial(number % 20)


def threaded(data):
    with ThreadPoolExecutor(max_workers=8) as executor:
        return list(executor.map(process_number, data))


def multiprocessing_pool(data):
    with mp.Pool(mp.cpu_count()) as pool:
        return pool.map(process_number, data)


def worker(input_queue, output_queue):
    while True:
        num = input_queue.get()
        if num is None:
            break
        result = process_number(num)
        output_queue.put(result)


def multiprocessing_manual(data):
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


def benchmark():
    data = generate_data(100_000)

    variants = [
        ("ThreadPoolExecutor", threaded),
        ("Multiprocessing.Pool", multiprocessing_pool),
        ("Manual multiprocessing", multiprocessing_manual),
    ]

    results_summary = []

    for name, func in variants:
        start = time.perf_counter()
        results = func(data)
        elapsed = time.perf_counter() - start

        print(f"{name:<25} | {elapsed} сек")
        results_summary.append((name, elapsed))

        with open(f"{name.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(results[:100], f, ensure_ascii=False, indent=2)

    print("\nСравнение времени выполнения:")
    print(f"{'Вариант':<25} | {'Время (сек)':>12}")
    for name, t in results_summary:
        print(f"{name:<25} | {t:>10}")


if __name__ == "__main__":
    benchmark()
