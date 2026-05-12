from django.db import models
from decimal import Decimal


class CorrectionEvent(models.Model):
    """
    Immutable audit record for ledger or wallet corrections.

    This is NOT a fix.
    This is a recorded intent that a correction occurred or is required.
    """

    CORRECTION_TYPES = (
        ("WALLET_DRIFT", "Wallet Drift"),
        ("LEDGER_DRIFT", "Ledger Drift"),
        ("SETTLEMENT_MISMATCH", "Settlement Mismatch"),
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
    )

    correction_type = models.CharField(
        max_length=64,
        choices=CORRECTION_TYPES,
    )

    expected = models.DecimalField(max_digits=12, decimal_places=2)
    actual = models.DecimalField(max_digits=12, decimal_places=2)
    difference = models.DecimalField(max_digits=12, decimal_places=2)

    delta_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=32,
        default="PENDING"
    )
    reason = models.CharField(max_length=255)

    resolved_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)