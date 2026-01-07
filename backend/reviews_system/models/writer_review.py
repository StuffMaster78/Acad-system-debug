from django.db import models
from reviews_system.models.base import ReviewBase
from django.conf import settings
from websites.models import Website
from orders.models import Order
from writer_management.models.profile import WriterProfile
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
        indexes = [
            models.Index(fields=['writer', 'submitted_at']),
            models.Index(fields=['website', 'submitted_at']),
            models.Index(fields=['writer', 'website', 'submitted_at']),
        ]


# class WriterRatingCooldown(models.Model):
#     """
#     Prevents clients from rating a writer until
#     the order is fully completed.
#     Cooldown period prevents rating abuse.
#     """
#     website = models.ForeignKey(
#         Website,
#         on_delete=models.CASCADE
#     )
#     order = models.OneToOneField(
#         Order, on_delete=models.CASCADE,
#         related_name="rating_cooldown"
#     )
#     writer = models.ForeignKey(
#         WriterProfile, on_delete=models.CASCADE,
#         related_name="rating_cooldowns"
#     )
#     cooldown_until = models.DateTimeField(
#         help_text="Time until the client can submit a rating."
#     )
#     rating_allowed = models.BooleanField(
#         default=False,
#         help_text="Has the cooldown expired?"
#     )

#     def __str__(self):
#         return (
#             f"Rating Cooldown for {self.writer.user.username}"
#             f" (Expires: {self.cooldown_until})"
#         )