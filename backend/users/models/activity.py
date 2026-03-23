from django.db import models


class UserActivity(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="activities",
    )

    activity_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)