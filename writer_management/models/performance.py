from django.db import models

from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from reviews_system.models.writer_review import WriterReview
from orders.models import Order

User = settings.AUTH_USER_MODEL

class WriterPerformance(models.Model):
    """
    Tracks performance metrics for writers.
    Includes average rating, completed orders, and pending orders.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_performance"
    )
    writer = models.OneToOneField(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="performance",
        help_text="The writer whose performance is being tracked."
    )
    average_rating = models.ForeignKey(
        WriterReview,
        on_delete=models.CASCADE,
        default=0.00,
        related_name="average_writer_rating",
        help_text="Average rating based on client feedback."
    )
    completed_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total number of completed orders."
    )
    pending_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total number of pending orders."
    )
    late_deliveries = models.PositiveIntegerField(
        default=0,
        help_text="Number of orders delivered late."
    )
    on_time_deliveries = models.PositiveIntegerField(
        default=0,
        help_text="Number of orders delivered on time." 
    )
    total_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total number of orders (completed + pending)."
    )
    total_earnings = models.PositiveIntegerField(
        default=0.00,
        help_text="Total amount the writer has earned"
    )
    total_disputed_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total number of disputed orders."
    )
    number_of_revisions = models.PositiveIntegerField(
        default=0,
        help_text="The number of revisions"
    )
    total_cancelled_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total number of cancelled orders."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the performance record was created."
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time the performance metrics were updated."
    )


    def __str__(self):
        return (
            f"Performance: {self.writer.user.username} - "
            f"Avg Rating: {self.average_rating}"
        )