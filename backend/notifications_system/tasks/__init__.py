"""
Import all task sub-modules so Celery autodiscover registers every task.
"""
from notifications_system.tasks import (  # noqa: F401
    maintenance,
    digest,
    send,
)
