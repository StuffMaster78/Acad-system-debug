from django.db import models
from django.utils.timezone import now


class EventOutbox(models.Model):
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)