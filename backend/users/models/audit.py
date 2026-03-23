from django.db import models


class UserAuditLog(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)