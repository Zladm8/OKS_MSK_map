'''
Обычно тут кроме таймера ничего и не лежит

'''
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"func {func.__name__} | Time {end - start:.4f} секунд")
        return result
    return wrapper