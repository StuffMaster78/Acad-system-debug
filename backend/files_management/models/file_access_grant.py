from django.conf import settings
from django.db import models

from files_management.enums import FileAccessAction


class FileAccessGrant(models.Model):
    """
    Represents explicit temporary or permanent access to a file.

    Access grants are useful when staff needs to expose a file outside
    the normal domain policy, for example during support resolution,
    dispute review, writer replacement, or temporary client access.

    Domain policies still remain the default authority. Grants are an
    escape hatch, not the main access system.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_access_grants",
    )

    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="access_grants",
    )

    attachment = models.ForeignKey(
        "files_management.FileAttachment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="access_grants",
    )

    grantee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="file_access_grants",
    )

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_file_access",
    )

    action = models.CharField(
        max_length=32,
        choices=FileAccessAction.choices,
        default=FileAccessAction.VIEW,
    )

    reason = models.TextField(
        blank=True,
        help_text="Reason access was granted.",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Empty means the grant does not expire automatically.",
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_file_access",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "grantee"]),
            models.Index(fields=["managed_file", "action"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["revoked_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.grantee.pk} can {self.action} {self.managed_file.pk}"