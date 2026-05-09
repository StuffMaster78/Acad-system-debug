from decimal import Decimal
from django.db import models
from django.utils.timezone import now


class AdvanceRequest(models.Model):
    """
    Writer requests early access to already-approved settlement funds.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"
        PAID = "PAID"

    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE)

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="advance_requests"
    )

    settlement_period = models.ForeignKey(
        "SettlementPeriod",
        on_delete=models.CASCADE,
        related_name="advances"
    )

    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)

    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.writer} | {self.requested_amount} | {self.status}"