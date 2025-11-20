import datetime
from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order

User = settings.AUTH_USER_MODEL

class OrderDispute(models.Model):
    """
    Writers can dispute an order.
    Admins must resolve the dispute.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="disputes"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_order_disputes"
    )
    reason = models.TextField(
        help_text="Reason for disputing the order."
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(
        blank=True, null=True,
        help_text="Admin notes on dispute resolution."
    )
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="dispute_resolutions"
    )

    def __str__(self):
        return f"Dispute: {self.writer.user.username} for Order {self.order.id} (Resolved: {self.resolved})"