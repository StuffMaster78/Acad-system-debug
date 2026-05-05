from __future__ import annotations

from django.db import models
from django.utils import timezone


class CommunicationThreadPolicy(models.Model):
    """
    Per website rules for a thread kind.

    Services should read this model when deciding if users can send
    messages, upload files, or communicate directly.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_thread_policies",
    )

    thread_kind = models.CharField(max_length=40)

    allow_client_messages = models.BooleanField(default=True)
    allow_writer_messages = models.BooleanField(default=True)
    allow_staff_messages = models.BooleanField(default=True)

    allow_attachments = models.BooleanField(default=True)
    require_attachment_moderation = models.BooleanField(default=False)
    require_message_moderation = models.BooleanField(default=False)

    auto_add_support = models.BooleanField(default=True)
    auto_add_assigned_writer = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread_kind"]),
            models.Index(fields=["website", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "thread_kind"],
                name="unique_communication_policy_per_thread_kind",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.website.pk} policy for {self.thread_kind}"