from django.db import models
from django.utils.timezone import now
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class WriterRewardCriteria(models.Model):
    """
    Admin-defined criteria for writer rewards (automated or manual).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="reward_criteria"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name of the reward criteria (e.g., 'Top Performer')."
    )
    min_completed_orders = models.PositiveIntegerField(
        default=10, help_text="Minimum orders required."
    )
    min_rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        default=4.5, help_text="Minimum rating required."
    )
    min_earnings = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=500.00, help_text="Minimum earnings required."
    )
    auto_reward_enabled = models.BooleanField(
        default=True, help_text="Enable automatic rewards."
    )

    def __str__(self):
        return f"Reward Criteria: {self.name} (Auto: {self.auto_reward_enabled})"

        
class WriterReward(models.Model):
    """
    Tracks rewards given to writers, including criteria, performance metrics, and prizes.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_reward"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="rewards",
        help_text="The writer receiving this reward."
    )
    criteria = models.ForeignKey(
        WriterRewardCriteria, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="rewards_given"
    )
    title = models.CharField(
        max_length=200,
        help_text="Custom title for the reward (e.g., 'Top Performer')."
    )
    performance_metric = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details of the performance metric used to determine the reward (e.g., ratings, urgent orders)."
    )
    awarded_date = models.DateTimeField(
        default=now, help_text="Date the reward was given."
    )
    prize = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Prize or benefit given to the writer (e.g., 'Bonus $50')."
    )
    notes = models.TextField(
        blank=True, null=True, 
        help_text="Additional notes about the reward."
    )

    def __str__(self):
        return f"{self.title} - {self.writer.user.username} ({self.awarded_date})"
    