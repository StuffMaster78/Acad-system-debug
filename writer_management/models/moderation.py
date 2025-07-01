from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order

User = settings.AUTH_USER_MODEL


class Probation(models.Model):
    """Tracks writers placed on probation."""
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_probation"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="probation_records"
    )
    placed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="probation_admins"
    )
    reason = models.TextField(
        help_text="Reason for probation."
    )
    start_date = models.DateTimeField(
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        help_text="Date when probation ends."
    )
    is_active = models.BooleanField(default=True)

    def check_expiry(self):
        """Automatically deactivates probation if the end_date has passed."""
        if self.end_date < now():
            self.is_active = False
            self.save()

    def __str__(self):
        return f"Probation: {self.writer.user.username} (Active: {self.is_active})"


class WriterPenalty(models.Model):
    """
    Logs penalties and fines applied to writers.
    """
    PENALTY_REASONS = [
        ("Late Submission", "Late Submission"),
        ("Plagiarism", "Plagiarism"),
        ("Missed Deadline", "Missed Deadline"),
        ("Client Complaint", "Client Complaint"),
        ("Other", "Other"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_penalty"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="penalties"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="writer_order_penalties"
    )
    reason = models.CharField(
        max_length=50, choices=PENALTY_REASONS,
        help_text="Reason for penalty."
    )
    amount_deducted = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Fine deducted from earnings."
    )
    applied_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="penalty_appliers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True, null=True,
        help_text="Additional notes."
    )

    def __str__(self):
        return f"Penalty: {self.writer.user.username} - {self.reason} (${self.amount_deducted})"


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