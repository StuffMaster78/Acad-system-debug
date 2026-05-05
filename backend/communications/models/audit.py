from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationAuditAction:
    """
    Auditable communication actions.
    """

    THREAD_CREATED = "thread_created"
    THREAD_LOCKED = "thread_locked"
    THREAD_CLOSED = "thread_closed"

    MESSAGE_CREATED = "message_created"
    MESSAGE_EDITED = "message_edited"
    MESSAGE_HIDDEN = "message_hidden"
    MESSAGE_DELETED = "message_deleted"
    MESSAGE_READ = "message_read"

    PARTICIPANT_ADDED = "participant_added"
    PARTICIPANT_REMOVED = "participant_removed"
  
    ATTACHMENT_ADDED = "attachment_added"
    ATTACHMENT_HIDDEN = "attachment_hidden"
    
    MODERATION_FLAGGED = "moderation_flagged"
    MODERATION_RESOLVED = "moderation_resolved"

    ESCALATION_CREATED = "escalation_created"
    ESCALATION_RESOLVED = "escalation_resolved"

    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"

    LINK_REVIEW_CREATED = "link_review_created"
    LINK_REVIEW_APPROVED = "link_review_approved"
    LINK_REVIEW_REJECTED = "link_review_rejected"
    LINK_REVIEW_BLOCKED = "link_review_blocked"

    CHOICES = (
        (THREAD_CREATED, "Thread created"),
        (THREAD_LOCKED, "Thread locked"),
        (THREAD_CLOSED, "Thread closed"),
        (MESSAGE_CREATED, "Message created"),
        (MESSAGE_EDITED, "Message edited"),
        (MESSAGE_HIDDEN, "Message hidden"),
        (MESSAGE_DELETED, "Message deleted"),
        (MESSAGE_READ, "Message read"),
        (PARTICIPANT_ADDED, "Participant added"),
        (PARTICIPANT_REMOVED, "Participant removed"),
        (ATTACHMENT_ADDED, "Attachment added"),
        (ATTACHMENT_HIDDEN, "Attachment hidden"),
        (MODERATION_FLAGGED, "Moderation flagged"),
        (MODERATION_RESOLVED, "Moderation resolved"),
        (ESCALATION_CREATED, "Escalation created"),
        (ESCALATION_RESOLVED, "Escalation resolved"),
        (TAG_ADDED, "Tag added"),
        (TAG_REMOVED, "Tag removed"),
        (LINK_REVIEW_CREATED, "Link review created"),
        (LINK_REVIEW_APPROVED, "Link review approved"),
        (LINK_REVIEW_REJECTED, "Link review rejected"),
        (LINK_REVIEW_BLOCKED, "Link review blocked"),
    )


class CommunicationAuditLog(models.Model):
    """
    Audit trail for important communication actions.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_audit_logs",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_audit_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=CommunicationAuditAction.CHOICES,
    )
    details = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "created_at"]),
            models.Index(fields=["website", "actor", "created_at"]),
            models.Index(fields=["website", "action", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} on thread {self.thread.pk}"