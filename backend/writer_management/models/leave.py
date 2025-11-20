from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()



class WriterLeave(models.Model):
    """
    Tracks periods when a writer is unavailable for work.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_leave"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="leaves",
        help_text="The writer who is unavailable."
    )
    start_date = models.DateTimeField(
        help_text="Start date of the leave period."
    )
    end_date = models.DateTimeField(
        help_text="End date of the leave period."
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for the leave (e.g., vacation, emergency)."
    )
    approved = models.BooleanField(
        default=False,
        help_text="Whether the leave has been approved by an admin."
    )

    def __str__(self):
        return f"Leave: {self.writer.user.username} ({self.start_date} - {self.end_date})"
    
    class Meta:
        verbose_name = "Writer Leave"
        verbose_name_plural = "Writer Leaves"
        ordering = ['start_date']


class WriterStrike(models.Model):
    """
    Records strikes against writers for policy violations.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_strikes"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="strikes",
        help_text="The writer who received the strike."
    )
    reason = models.TextField(
        help_text="Reason for the strike."
    )
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_strikes"
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the strike was issued."
    )

    def __str__(self):
        return f"Strike: {self.writer.user.username} - {self.reason[:50]}..."
    
    class Meta:
        verbose_name = "Writer Strike"
        verbose_name_plural = "Writer Strikes"
        ordering = ['-issued_at']

class WriterLeaveHistory(models.Model):
    """
    Tracks changes to writer leave requests.
    Useful for auditing and tracking leave history.
    """
    leave = models.ForeignKey(
        WriterLeave, on_delete=models.CASCADE,
        related_name="history"
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="leave_history_changes"
    )
    change_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the change was made."
    )
    change_type = models.CharField(
        max_length=50, 
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")],
        help_text="Type of change made."
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="Details about the change."
    )

    def __str__(self):
        return f"Leave History: {self.leave.writer.user.username} ({self.change_type})"
    
    class Meta:
        verbose_name = "Writer Leave History"
        verbose_name_plural = "Writer Leave Histories"
        ordering = ['-change_date']


class WriterStrikeHistory(models.Model):
    """
    Tracks changes to writer strikes.
    Useful for auditing and tracking strike history.
    """
    strike = models.ForeignKey(
        WriterStrike, on_delete=models.CASCADE,
        related_name="history"
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="strike_history_changes"
    )
    change_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the change was made."
    )
    change_type = models.CharField(
        max_length=50, 
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")],
        help_text="Type of change made."
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="Details about the change."
    )

    def __str__(self):
        return f"Strike History: {self.strike.writer.user.username} ({self.change_type})"

    class Meta:
        verbose_name = "Writer Strike History"
        verbose_name_plural = "Writer Strike Histories"
        ordering = ['-change_date']

class WriterLeaveAdminReview(models.Model):
    """
    Admin reviews for writer leave requests.
    Admins can provide feedback on leave requests.
    """
    leave = models.ForeignKey(
        WriterLeave, on_delete=models.CASCADE,
        related_name="admin_reviews"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="leave_admin_reviews"
    )
    review_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(
        blank=True, null=True,
        help_text="Admin comments on the leave request."
    )

    def __str__(self):
        return f"Leave Review: {self.leave.writer.user.username} ({self.review_date})"
    
    class Meta:
        verbose_name = "Writer Leave Admin Review"
        verbose_name_plural = "Writer Leave Admin Reviews"
        ordering = ['-review_date']