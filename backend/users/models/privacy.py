from django.db import models


class PrivacySettings(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="privacy_settings",
    )

    profile_visible = models.BooleanField(default=True)
    email_visible = models.BooleanField(default=False)


class DataAccessLog(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="data_access_logs",
    )

    accessed_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=255)


class DeletionSettings(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="deletion_settings",
    )

    scheduled_for_deletion = models.BooleanField(default=False)