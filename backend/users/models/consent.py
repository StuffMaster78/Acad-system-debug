from django.db import models


class UserConsent(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="consents",
    )

    consent_type = models.CharField(max_length=255)
    granted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)