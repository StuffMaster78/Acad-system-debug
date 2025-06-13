from django.db import models
from django.conf import settings


class SecurityAlertLog(models.Model):
    """
    Logs suspicious device activity or anomalous login behavior.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_alerts"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="security_alerts"
    )
    fingerprint = models.ForeignKey(
        "authentication.DeviceFingerprint",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="alerts"
    )
    reasons = models.TextField(
        help_text="Reasons this activity was flagged as suspicious."
    )
    severity = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.user} @ {self.timestamp} (sev={self.severity})"