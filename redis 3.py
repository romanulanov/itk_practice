import time
import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self, key="api_rate_limiter", window_seconds=3, max_requests=5):
        self.redis = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        self.key = key
        self.window = window_seconds
        self.limit = max_requests

    def test(self) -> bool:
        now = time.time()
        self.redis.zremrangebyscore(self.key, 0, now - self.window)
        current_count = self.redis.zcard(self.key)

        if current_count < self.limit:
            self.redis.zadd(self.key, {str(now): now})
            self.redis.expire(self.key, self.window)
            return True
        else:
            return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        pass


if __name__ == "__main__":
    import random

    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
