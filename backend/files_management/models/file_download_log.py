from django.db import models


class FileDownloadLog(models.Model):
    """
    Records download activity for auditing and analytics.

    This is critical for:
    - disputes
    - security audits
    - compliance
    """

    file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="download_logs",
    )

    downloaded_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(blank=True)

    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["downloaded_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.file} downloaded at {self.downloaded_at}"