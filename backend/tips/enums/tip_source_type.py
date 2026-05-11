from __future__ import annotations

from django.db.models import TextChoices


class TipSourceType(TextChoices):
    """
    Defines the funding source used for a tip.
    """

    WALLET = "wallet", "Wallet"
    EXTERNAL = "external", "External"