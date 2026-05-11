from __future__ import annotations

from django.db.models import TextChoices


class TipEvents(TextChoices):

    CREATED = "tip.created", "Tip Created"

    PAYMENT_INITIATED = (
        "tip.payment_initiated",
        "Tip Payment Initiated",
    )

    PROCESSING = "tip.processing", "Tip Processing"

    SUCCEEDED = "tip.succeeded", "Tip Succeeded"

    FAILED = "tip.failed", "Tip Failed"

    CANCELLED = "tip.cancelled", "Tip Cancelled"

    WALLET_HOLD_CREATED = (
        "wallet.hold.created",
        "Wallet Hold Created",
    )

    WALLET_HOLD_CAPTURED = (
        "wallet.hold.captured",
        "Wallet Hold Captured",
    )

    WALLET_HOLD_RELEASED = (
        "wallet.hold.released",
        "Wallet Hold Released",
    )