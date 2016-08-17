from redis import StrictRedis


redis = StrictRedis(host='redis', port=6379, db=0)


def get(key, default=None):
    if redis.exists(key):
        return redis.get(key)
    else:
        return default


def save(key, value):
    return redis.set(key, value)


def flush():
    redis.flushdb()
