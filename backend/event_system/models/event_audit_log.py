import uuid
from django.db import models


class EventAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event_id = models.UUIDField(db_index=True)

    event_type = models.CharField(max_length=120)

    stage = models.CharField(max_length=50)
    """
    stages:
        - published
        - claimed
        - dispatched
        - failed
        - retried
        - dead_letter
    """

    message = models.TextField(blank=True)
    worker_id = models.CharField(max_length=100, null=True, blank=True)
    duration_ms = models.IntegerField(null=True)
    correlation_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    retry_count = models.PositiveIntegerField(null=True, blank=True)
    event_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)