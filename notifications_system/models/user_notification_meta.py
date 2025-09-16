# notifications_system/models/user_notification_meta.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class UserNotificationMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notif_meta")
    # If you’re multi-tenant per-website, make this a FK instead (user+website unique_together).
    last_seen_at = models.DateTimeField(default=timezone.now)

    def touch(self):
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at"])

    def __str__(self):
        return f"UserNotificationMeta<{self.user_id}>"
    class Meta:
        verbose_name = "User Notification Meta"
        verbose_name_plural = "User Notification Metas"
        db_table = "user_notification_meta"