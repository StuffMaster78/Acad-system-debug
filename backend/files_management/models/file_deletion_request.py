from django.conf import settings
from django.db import models

from files_management.enums import (
    DeletionRequestScope,
    DeletionRequestStatus,
)


class FileDeletionRequest(models.Model):
    """
    Represents a governed request to remove a file attachment or file.

    Clients and writers must not directly delete uploaded files. They
    request deletion. Staff then approves, rejects, or completes the
    request based on business context, retention policy, and evidence
    value.

    Requests target attachments first because the same file may be
    reused in several places. Removing one attachment is safer than
    deleting the physical file everywhere.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_deletion_requests",
    )

    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="deletion_requests",
    )

    attachment = models.ForeignKey(
        "files_management.FileAttachment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deletion_requests",
    )
    external_link = models.ForeignKey(
        "files_management.ExternalFileLink",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="deletion_requests",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_deletion_requests",
    )

    reason = models.TextField(
        help_text="Reason supplied by the requester.",
    )

    scope = models.CharField(
        max_length=32,
        choices=DeletionRequestScope.choices,
        default=DeletionRequestScope.DETACH_ONLY,
    )

    status = models.CharField(
        max_length=32,
        choices=DeletionRequestStatus.choices,
        default=DeletionRequestStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_file_deletion_requests",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    admin_comment = models.TextField(
        blank=True,
        help_text="Internal staff decision note.",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["scope"]),
            models.Index(fields=["created_at"]),
        ]

        constraints = [
            models.CheckConstraint(
                name="file_deletion_request_has_source",
                check=(
                    models.Q(managed_file__isnull=False)
                    | models.Q(external_link__isnull=False)
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"Deletion request for {self.managed_file.pk}"