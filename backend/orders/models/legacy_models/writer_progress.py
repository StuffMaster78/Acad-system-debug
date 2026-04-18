from django.apps import apps
from django.conf import settings
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from datetime import timedelta
from django.db import models
from django.utils import timezone
from orders.models.orders import Order

User = settings.AUTH_USER_MODEL 

class WriterProgress(models.Model):
    """
    Tracks progress logs for writers working on orders.
    Includes notes, screened word checking, and admin moderation.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='writer_progress'
    )
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="progress_logs",
        limit_choices_to={"role": "writer"},
        help_text="The writer associated with this progress log."
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="progress_logs",
        help_text="The order associated with this progress log."
    )
    progress_percentage = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)],
        help_text="Percentage of work completed (0-100)."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about the progress update."
    )
    # Moderation fields
    is_withdrawn = models.BooleanField(
        default=False,
        help_text="Whether this progress report has been withdrawn by admin due to policy violations."
    )
    withdrawn_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawn_progress_reports",
        help_text="Admin/superadmin who withdrew this report."
    )
    withdrawn_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this report was withdrawn."
    )
    withdrawal_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for withdrawal (e.g., screened words detected)."
    )
    # Flag for screened words
    contains_screened_words = models.BooleanField(
        default=False,
        help_text="Whether this report contains screened words."
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_screened_words(self):
        """Check if notes contain screened words."""
        if not self.notes:
            return False
        
        from communications.models import ScreenedWord
        screened_words = ScreenedWord.objects.values_list('word', flat=True)
        
        notes_lower = self.notes.lower()
        for word in screened_words:
            if word.lower() in notes_lower:
                self.contains_screened_words = True
                return True
        
        self.contains_screened_words = False
        return False
    
    def withdraw(self, withdrawn_by, reason=None):
        """Withdraw this progress report."""
        self.is_withdrawn = True
        self.withdrawn_by = withdrawn_by
        self.withdrawn_at = timezone.now()
        if reason:
            self.withdrawal_reason = reason
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to check for screened words."""
        if self.notes:
            self.check_screened_words()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['order', '-timestamp']),
            models.Index(fields=['writer', '-timestamp']),
            models.Index(fields=['is_withdrawn']),
        ]

    def __str__(self):
        status = " (Withdrawn)" if self.is_withdrawn else ""
        return (
            f"Progress {self.progress_percentage}% for Order {self.order.id} "
            f"by {self.writer.username}{status}"
        )
