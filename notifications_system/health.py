# notifications_system/health.py
from django.db import connection
from .redis_health import check_redis_health

def check_db():
    with connection.cursor() as c:
        c.execute("SELECT 1;")
        return True

def healthy():
    return {
        "db": check_db(),
        "redis": check_redis_health(),
        "celery": True,  # optionally implement a ping job/update a cache key
    }
def is_healthy():
    status = healthy()
    return all(status.values())
    