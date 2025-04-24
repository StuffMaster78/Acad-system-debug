from django.db import models
from django.conf import settings
from django.utils.timezone import now
import uuid

class RegistrationToken(models.Model):
    """
    Handles registration of new users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    created_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.token}"