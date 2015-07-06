import zlib
import time

def benchmark():
    start = time.time()
    iterations = 0
    while time.time() - start < 1:
        zlib.compress("abcd"*10000,9)
        iterations += 1
    return (iterations / (time.time() - start))