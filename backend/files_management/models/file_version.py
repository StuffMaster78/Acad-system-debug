from django.db import models


class FileVersion(models.Model):
    """
    Tracks versions of a ManagedFile.

    This allows safe replacement of files such as drafts,
    final submissions, or profile images.
    """

    file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="versions",
    )

    version_number = models.PositiveIntegerField()

    replaced_file = models.ForeignKey(
        "files_management.ManagedFile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replaced_by_versions",
    )

    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("file", "version_number")
        ordering = ["-version_number"]

    def __str__(self) -> str:
        return f"{self.file} v{self.version_number}"