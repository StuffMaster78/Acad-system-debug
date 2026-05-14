from django.db import models


class ReviewTarget(models.TextChoices):
    """
    Defines all supported review target types.

    This is the canonical business vocabulary
    for what can be reviewed.
    """

    ORDER = "order", "Order"
    SPECIAL_ORDER = "special_order", "Special Order"
    CLASS_ORDER = "class_order", "Class Order"
    WEBSITE = "website", "Website"