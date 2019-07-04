import multiprocessing as mp
import sys


def power_of_two(n: int) -> (int, int):
    print(f"Power of two: {n}")
    result = 1
    for i in range(1, n):
        result *= 2

    return n, result


def collect_results(n, result):
    global results

    results[n] = result


if __name__ == '__main__':
    print("Number of processors: ", mp.cpu_count())
    pool = mp.Pool(mp.cpu_count())
    max_n = 10
    results = []
    for i in range(0, max_n):
        results.append(0)

    # for i in range(0, max_n):
    #     pool.apply_async(power_of_two, args=(i,), callback=collect_results)

    # results = [pool.apply(power_of_two, args=(i, 1)) for i in range(0, max_n)]
    results = pool.map(power_of_two, [i for i in range(0, max_n)])

    pool.close()
    # pool.join()

    print(results)
else:
    print(mp.current_process())
