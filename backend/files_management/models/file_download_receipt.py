from django.conf import settings
from django.db import models


class FileDownloadReceipt(models.Model):
    """
    Tracks the first time each user downloads a FileAttachment.

    FileAttachment.first_downloaded_at records the global first download
    (by anyone). This model records per-user first downloads so that one
    user's download does not clear another user's "new file" badge.
    """

    attachment = models.ForeignKey(
        "files_management.FileAttachment",
        on_delete=models.CASCADE,
        related_name="download_receipts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="file_download_receipts",
    )
    first_downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "files_management_download_receipt"
        unique_together = ("attachment", "user")
        indexes = [
            models.Index(
                fields=["attachment", "user"],
                name="fm_receipt_attach_user_idx",
            ),
            models.Index(
                fields=["user"],
                name="fm_receipt_user_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → attachment #{self.attachment_id}"
