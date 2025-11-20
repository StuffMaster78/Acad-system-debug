from django.db import models
from django.conf import settings
from websites.models import Website
from django.contrib.auth import get_user_model
from writer_management.models.profile import WriterProfile
from orders.models import Order

User = get_user_model()


class WriterMessageThread(models.Model):
    """
    A thread for writer messages.
    Each order has a writer-client and/or writer-admin thread.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="message_threads"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="message_threads"
    )
    participant = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="writer_participant_threads",
        help_text="The client or admin participating in the thread."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message Thread for Order {self.order.id} - {self.writer.user.username} & {self.participant.username}"
    
class WriterMessage(models.Model):
    """
    Messages exchanged between a writer and a client/admin in an order thread.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    thread = models.ForeignKey(
        WriterMessageThread, on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="sent_writer_messages"
    )
    content = models.TextField(help_text="Message content.")
    attachment = models.FileField(
        upload_to="writer_messages/",
        blank=True, null=True,
        help_text="Optional message attachment."
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(
        default=False,
        help_text="Flagged for admin moderation."
    )

    def __str__(self):
        return f"Message from {self.sender.username} in Thread {self.thread.id} (Flagged: {self.flagged})"


class WriterMessageModeration(models.Model):
    """
    Stores flagged messages for admin review.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        WriterMessage, on_delete=models.CASCADE,
        related_name="moderation"
    )
    flagged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="moderated_messages"
    )
    reason = models.TextField(help_text="Reason for flagging the message.")
    reviewed = models.BooleanField(
        default=False,
        help_text="Has the admin reviewed this message?"
    )
    action_taken = models.CharField(
        max_length=50, 
        choices=[
            ("Delete", "Delete"),
            ("Warn Writer", "Warn Writer"),
            ("No Action", "No Action"),
        ],
        blank=True, null=True
    )

    def __str__(self):
        return f"Moderation - {self.message.id} (Reviewed: {self.reviewed})"