from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from files_management.enums import FilePurpose, FileVisibility


class FileAttachment(models.Model):
    """
    Links an uploaded file or external file link to a domain object.

    This model is the central bridge between files and business objects.
    It allows files to be attached to orders, messages, profiles, CMS
    pages, support tickets, classes, payment records, and future domains.

    An attachment must point to exactly one file source:

    1. managed_file for files uploaded into platform storage.
    2. external_link for Google Docs, Google Slides, Drive links,
       Dropbox links, Loom videos, and similar remote resources.

    This model should stay dumb. It stores relationships and metadata.
    Business access rules belong in services and policy classes.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_attachments",
    )

    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )

    external_link = models.ForeignKey(
        "files_management.ExternalFileLink",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    object_id = models.PositiveBigIntegerField()

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )
    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="deletion_requests",
    )
    purpose = models.CharField(
        max_length=64,
        choices=FilePurpose.choices,
    )

    visibility = models.CharField(
        max_length=64,
        choices=FileVisibility.choices,
        default=FileVisibility.PRIVATE,
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Marks this as the main file for the target object.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Inactive attachments are hidden from normal flows.",
    )

    attached_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="file_attachments",
    )

    display_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional display label for this attachment.",
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional staff or system notes about this attachment.",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible context metadata for domain integrations.",
    )

    attached_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-attached_at"]
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["purpose"]),
            models.Index(fields=["visibility"]),
            models.Index(fields=["attached_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="file_attachment_exactly_one_source",
                check=(
                    (
                        models.Q(managed_file__isnull=False)
                        & models.Q(external_link__isnull=True)
                    )
                    | (
                        models.Q(managed_file__isnull=True)
                        & models.Q(external_link__isnull=False)
                    )
                ),
            ),
        ]

    def clean(self) -> None:
        """
        Validate that the attachment has exactly one file source.

        This mirrors the database constraint and gives cleaner errors in
        admin, serializers, tests, and service level validation.
        """

        has_managed_file = self.managed_file.pk is not None
        has_external_link = self.external_link.pk is not None

        if has_managed_file == has_external_link:
            raise ValidationError(
                "A file attachment must reference exactly one file "
                "source."
            )

        if self.managed_file and self.managed_file.website_id != self.website.id:
            raise ValidationError(
                "Managed file must belong to the same website."
            )

        if self.external_link:
            if self.external_link.website_id != self.website.id:
                raise ValidationError(
                    "External file link must belong to the same website."
                )

    @property
    def source(self):
        """
        Return the attached source object.

        This is intentionally lightweight and should not be used to make
        authorization decisions.
        """

        return self.managed_file or self.external_link

    def __str__(self) -> str:
        source_label = self.display_name or str(self.source)
        return f"{source_label} attached to {self.content_type.pk}"