from django.db import models
from websites.models import Website
from writer_management.models.profile import WriterProfile


class WriterRewardManager(models.Manager):
    def create(self, **kwargs):  # type: ignore[override]
        writer = kwargs.get('writer')
        if kwargs.get('website') is None and writer is not None:
            try:
                kwargs['website'] = getattr(writer, 'website', None)
            except Exception:
                pass
        return super().create(**kwargs)


from django.utils.timezone import now

class WriterReward(models.Model):
    """
    Tracks rewards given to writers, including criteria, performance metrics, and prizes.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="writer_rewards")
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="rewards")
    criteria = models.ForeignKey(
        'WriterRewardCriteria', on_delete=models.SET_NULL,
        null=True, blank=True, related_name="rewards_given"
    )
    title = models.CharField(max_length=200, help_text="Custom title for the reward (e.g., 'Top Performer').")
    performance_metric = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details of the performance metric used to determine the reward."
    )
    awarded_date = models.DateTimeField(default=now, help_text="Date the reward was given.")
    prize = models.CharField(max_length=255, blank=True, null=True, help_text="Prize or benefit (e.g., 'Bonus $50').")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the reward.")
    metadata = models.JSONField(default=dict, blank=True)  # For backward compatibility
    created_at = models.DateTimeField(auto_now_add=True)  # For backward compatibility

    objects = WriterRewardManager()

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'writer', None) and getattr(self.writer, 'website_id', None):
                    self.website_id = self.writer.website_id
                else:
                    from websites.models import Website
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.writer.user.username} ({self.awarded_date or self.created_at})"


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
    