from django.db import models
from reviews_system.models.base import ReviewBase
from django.conf import settings

class OrderReview(ReviewBase):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_reviews_written_by"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="order_reviews"
    )

    class Meta:
        unique_together = ("reviewer", "order")
        ordering = ["-submitted_at"]
