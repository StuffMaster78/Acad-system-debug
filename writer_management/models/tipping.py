from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order


class Tip(models.Model):
    """
    Represents a tip sent by a client to a writer for an order.
    """
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="tips_sent"
    )
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="tips_received"
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="tips"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        help_text="Multitenancy support: this tip is for a specific website.",
    )
    tip_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tip_reason = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    writer_percentage = models.ForeignKey(
        'writer_management.WriterLevel',
        on_delete=models.CASCADE,
        related_name="tips"
    )
    writer_earning = models.DecimalField(max_digits=10, decimal_places=2)
    platform_profit = models.DecimalField(max_digits=10, decimal_places=2)