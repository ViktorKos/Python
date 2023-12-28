import concurrent.futures
import multiprocessing

def factorize_parallel(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors

def factorize_all_parallel(numbers):
    result = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        result = list(executor.map(factorize_parallel, numbers))
    return result