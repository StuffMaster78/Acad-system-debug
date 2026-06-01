"""
Import all task sub-modules so Celery autodiscover registers every task.
"""
from payments_processor.tasks import (  # noqa: F401
    payment_application_tasks,
    payment_cleanup_tasks,
    payment_reconciliation_tasks,
    pending_payment_resolution_tasks,
    refund_tasks,
)
