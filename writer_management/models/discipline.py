from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order
from django.utils.timezone import now

User = get_user_model()


class WriterDisciplineConfig(models.Model):
    """
    Configuration for writer discipline enforcement.
    Admins can set how many strikes trigger suspension or blacklisting.
    """
    website = models.OneToOneField(
        Website, on_delete=models.CASCADE
    )
    max_strikes = models.PositiveIntegerField(
        default=3,
        help_text="Strikes before a warning is escalated."
    )
    auto_suspend_days = models.PositiveIntegerField(
        default=7,
        help_text="Auto suspension duration (in days)."
    )
    auto_blacklist_strikes = models.PositiveIntegerField(default=5, help_text="Strikes before blacklisting.")

    def __str__(self):
        return f"Discipline Config for {self.website.name}"

    class Meta:
        verbose_name = "Writer Discipline Configuration"
        verbose_name_plural = "Writer Discipline Configurations"


class WriterStrike(models.Model):
    """
    Records disciplinary strikes against writers.
    Acts as warnings for policy violations.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="writer_strikes"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="strikes",
        help_text="Writer receiving the strike."
    )
    reason = models.TextField(help_text="Reason for the strike.")
    issued_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="issued_strikes"
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Strike: {self.writer.user.username} - {self.reason[:50]}..."

    class Meta:
        verbose_name = "Writer Strike"
        verbose_name_plural = "Writer Strikes"
        ordering = ['-issued_at']


class WriterStrikeHistory(models.Model):
    """
    Tracks changes made to WriterStrike instances.
    Supports auditing and rollback understanding.
    """
    strike = models.ForeignKey(
        WriterStrike, on_delete=models.CASCADE,
        related_name="history"
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="strike_history_changes"
    )
    change_date = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(
        max_length=50,
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")]
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Strike History: {self.strike.writer.user.username} ({self.change_type})"

    class Meta:
        verbose_name = "Writer Strike History"
        verbose_name_plural = "Writer Strike Histories"
        ordering = ['-change_date']

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
    auto_triggered = models.BooleanField(default=False)
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
    
    class Meta:
        verbose_name = "Writer Suspension"
        verbose_name_plural = "Writer Suspensions"
        ordering = ['-start_date']
        unique_together = ('website', 'writer', 'is_active')

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'writer', None) and getattr(self.writer, 'website_id', None):
                    self.website_id = self.writer.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)

class WriterSuspensionHistory(models.Model):
    """
    Tracks changes made to WriterSuspension instances.
    Useful for auditing and understanding suspension history.
    """
    suspension = models.ForeignKey(
        WriterSuspension, on_delete=models.CASCADE,
        related_name="history"
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="suspension_history_changes"
    )
    change_date = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(
        max_length=50,
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")]
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Suspension History: {self.suspension.writer.user.username} ({self.change_type})"

    class Meta:
        verbose_name = "Writer Suspension History"
        verbose_name_plural = "Writer Suspension Histories"
        ordering = ['-change_date']



class WriterBlacklist(models.Model):
    """
    Permanently or temporarily blacklists a writer.
    Prevents access to new orders or platform features.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="blacklist_entries"
    )
    reason = models.TextField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    auto_triggered = models.BooleanField(default=False)
    blacklisted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="writer_blacklists"
    )

    def __str__(self):
        return f"Blacklisted: {self.writer.user.username} ({'Auto' if self.auto_triggered else 'Manual'})"

    class Meta:
        verbose_name = "Writer Blacklist"
        verbose_name_plural = "Writer Blacklists"
        ordering = ['-blacklisted_at']
        unique_together = ('website', 'writer', 'is_active')


class WriterBlacklistHistory(models.Model):
    """
    Tracks changes to blacklisting status of a writer.
    Useful for audit logs.
    """
    blacklist = models.ForeignKey(
        WriterBlacklist, on_delete=models.CASCADE,
        related_name="history"
    )
    change_type = models.CharField(
        max_length=50,
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Revoked", "Revoked")]
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="blacklist_history_changes"
    )
    notes = models.TextField(blank=True, null=True)
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklist History: {self.blacklist.writer.user.username} ({self.change_type})"

    class Meta:
        verbose_name = "Writer Blacklist History"
        verbose_name_plural = "Writer Blacklist Histories"
        ordering = ['-change_date']


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

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'writer', None) and getattr(self.writer, 'website_id', None):
                    self.website_id = self.writer.website_id
                elif getattr(self, 'order', None) and getattr(self.order, 'website_id', None):
                    self.website_id = self.order.website_id
            except Exception:
                pass
        super().save(*args, **kwargs)