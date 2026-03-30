from django.db import models


class UserPermission(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="permissions",
    )

    permission_name = models.CharField(max_length=255)