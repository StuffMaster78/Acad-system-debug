from django.db import models

from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order

User = settings.AUTH_USER_MODEL    

class WriterRatingCooldown(models.Model):
    """
    Prevents clients from rating a writer until the order is fully completed.
    Cooldown period prevents rating abuse.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE,
        related_name="rating_cooldown"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="rating_cooldowns"
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