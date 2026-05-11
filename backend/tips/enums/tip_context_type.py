from __future__ import annotations

from django.db.models import TextChoices


class TipContextType(TextChoices):
    """
    Defines the domain context associated with a tip.
    """

    ORDER = "order", "Order"
    CLASS = "class", "Class"
    SPECIAL_ORDER = "special_order", "Special Order"
    WRITER = "writer", "Writer"
    OTHER = "other", "Other"