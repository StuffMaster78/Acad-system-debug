from django.db import models
from reviews_system.models.base import ReviewBase
from django.conf import settings

class WriterReview(ReviewBase):
    """Model for reviews written by clients about writers."""
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="writer_reviews"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="writer_reviews"
    )

    class Meta:
        ordering = ["-submitted_at"]