import json
import redis


class RedisQueue:
    def __init__(self, name="default_queue", host="localhost", port=6379, db=0):
        self.name = name
        self.redis = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def publish(self, msg: dict):
        self.redis.rpush(self.name, json.dumps(msg))

    def consume(self) -> dict | None:
        data = self.redis.lpop(self.name)
        if data is None:
            return None
        return json.loads(data)


if __name__ == "__main__":
    q = RedisQueue()

    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}
    assert q.consume() is None
