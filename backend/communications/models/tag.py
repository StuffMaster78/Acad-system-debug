from __future__ import annotations

from django.db import models
from django.utils import timezone


class CommunicationThreadTag(models.Model):
    """
    Tenant scoped label used to organize communication threads.

    Examples:
        urgent
        payment issue
        needs admin
        revision
        writer delay
        sensitive
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_thread_tags",
    )

    name = models.CharField(max_length=80)
    color = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_communication_thread_tag_per_website",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class CommunicationThreadTagAssignment(models.Model):
    """
    Links a tag to a communication thread.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_thread_tag_assignments",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="tag_assignments",
    )
    tag = models.ForeignKey(
        "communications.CommunicationThreadTag",
        on_delete=models.CASCADE,
        related_name="thread_assignments",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread"]),
            models.Index(fields=["website", "tag"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["thread", "tag"],
                name="unique_communication_tag_assignment",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tag.pk} on thread {self.thread.pk}"