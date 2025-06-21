from django.db import models
from reviews_system.models.base import ReviewBase

class WebsiteReview(ReviewBase):
    """Model for reviews written by clients about websites."""
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    class Meta:
        unique_together = ("reviewer", "website")  # one review per user per site
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.reviewer.username} - {self.rating} stars for {self.website.name}"