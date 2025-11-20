from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from orders.models import Order
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from fines.models import Fine
from writer_management.models.profile import WriterProfile

User = settings.AUTH_USER_MODEL

class WriterRating(models.Model):
    """
    Tracks client ratings and feedback for writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_rating"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="ratings",
        help_text="The writer being rated."
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings_given",
        limit_choices_to={"role": "client"},
        help_text="The client providing the rating."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="writer_ratings_on_orders",
        help_text="The order associated with this rating."
    )
    rating = models.PositiveIntegerField(
        help_text="Rating given by the client (1 to 5).",
        choices=[(i, str(i)) for i in range(1, 6)]  # Ratings from 1 to 5
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Optional feedback provided by the client."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the rating was created.")

    def __str__(self):
        return f"Rating {self.rating} for {self.writer.user.username} by {self.client.username} (Order {self.order.id})"
    

class WriterRatingCooldown(models.Model):
    """
    Prevents clients from rating a writer until the order is fully completed.
    Cooldown period prevents rating abuse.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="wt_rating_cooldown"
    )
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE,
        related_name="rating_cooldown"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="writer_rating_cooldowns"
    )
    cooldown_until = models.DateTimeField(
        help_text="Time until the client can submit a rating."
    )
    rating_allowed = models.BooleanField(
        default=False,
        help_text="Has the cooldown expired?"
    )

    def __str__(self):
        return f"Rating Cooldown for {self.writer.user.username} (Expires: {self.cooldown_until})"
    

class WriterRatingFeedback(models.Model):
    """
    Stores feedback comments for a specific writer rating.
    """
    rating = models.ForeignKey(
        WriterRating,
        on_delete=models.CASCADE,
        related_name="feedback_for_specific_writer_rating"
    )
    comment = models.TextField(
        help_text="Feedback comment provided by the client."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.rating.writer.user.username} (Order {self.rating.order.id})"