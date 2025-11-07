import datetime
import functools
import redis
import time


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"single_lock:{func.__name__}"
            lock_value = str(time.time())

            lock_ttl = int(max_processing_time.total_seconds() * 1000)

            acquired = redis_client.set(lock_key, lock_value, nx=True, px=lock_ttl)
            if not acquired:
                raise RuntimeError(f"Функция '{func.__name__}' уже где-то запущена.")

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                current_value = redis_client.get(lock_key)
                if current_value and current_value.decode() == lock_value:
                    redis_client.delete(lock_key)

        return wrapper
    return decorator
