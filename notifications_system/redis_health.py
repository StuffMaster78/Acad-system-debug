import redis
from django.conf import settings

def check_redis_health():
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        return r.ping()
    except redis.RedisError:
        return False