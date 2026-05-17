from django.db import models


class ReviewTarget(models.TextChoices):
    """Supported review target types."""

    ORDER = "order", "Order"
    SPECIAL_ORDER = "special_order", "Special Order"
    CLASS_ORDER = "class_order", "Class Order"
    WEBSITE = "website", "Website"