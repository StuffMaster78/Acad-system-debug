from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order

User = settings.AUTH_USER_MODEL


class WriterSuspension(models.Model):
    """
    Tracks suspended writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_suspension"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="suspensions"
    )
    reason = models.TextField(help_text="Reason for suspension.")
    suspended_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="suspension_admins"
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(
        blank=True, null=True,
        help_text="Optional end date for temporary suspensions."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="If True, the writer is currently suspended."
    )

    def lift_suspension(self):
        """
        Admin can manually lift a suspension.
        """
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Suspension: {self.writer.user.username} (Active: {self.is_active})"