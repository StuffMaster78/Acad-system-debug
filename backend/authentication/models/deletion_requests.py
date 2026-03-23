from django.db import models
from django.conf import settings
from django.utils import timezone


class AccountDeletionRequest(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (REJECTED, 'Rejected'),
    ]
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='deletion_requests_website',
        help_text="The website where the request is coming from"
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='deletion_requests'
    )
    request_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    confirmation_time = models.DateTimeField(
        null=True,
        blank=True
    )
    rejection_time = models.DateTimeField(
        null=True,
        blank=True
    )
    scheduled_deletion_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time after which user will be permanently deleted."
    )
    undo_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True
    )
    undo_token_expiry = models.DateTimeField(
        null=True,
        blank=True
    )
    reason = models.TextField(null=True, blank=True)
    
    def confirm(self):
        """Confirm the deletion request without scheduling."""
        self.status = self.CONFIRMED
        self.confirmation_time = timezone.now()
        self.save(update_fields=['status', 'confirmation_time'])
    
    def reject(self):
        """Reject the deletion request."""
        self.status = self.REJECTED
        self.rejection_time = timezone.now()
        self.save(update_fields=['status', 'rejection_time'])

    def schedule_deletion(self, delay_hours=72):
        """Confirm and schedule the user for deletion after a delay."""
        self.status = self.CONFIRMED
        self.confirmation_time = timezone.now()
        self.scheduled_deletion_time = self.confirmation_time + timezone.timedelta(hours=delay_hours)
        self.save(update_fields=['status', 'confirmation_time', 'scheduled_deletion_time'])

    def generate_undo_token(self):
        """Generate a secure token allowing the user to cancel deletion."""
        import secrets
        self.undo_token = secrets.token_urlsafe(32)
        self.undo_token_expiry = timezone.now() + timezone.timedelta(hours=72)
        self.save(update_fields=['undo_token', 'undo_token_expiry'])

    def is_undo_token_valid(self):
        """Check whether the undo token is still usable."""
        return (
            self.undo_token is not None
            and self.undo_token_expiry is not None
            and timezone.now() < self.undo_token_expiry
        )

    def perform_soft_delete(self):
        """Deactivate the user account without deleting the record."""
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
    
    def __str__(self):
        return f"Deletion request for {self.user.username} ({self.get_status_display()})"

    class Meta:
        ordering = ['-request_time']
        indexes = [
            models.Index(fields=['status', 'scheduled_deletion_time']),
        ]  


class DeletionRequestManager(models.Manager):
    """Manager for AccountDeletionRequest model."""
    def pending_requests(self):
        """
        Return all deletion requests with 'pending' status.
        """
        return self.filter(status=AccountDeletionRequest.PENDING)
    
    def confirmed_requests(self):
        """
        Return all deletion requests with 'confirmed' status.
        """
        return self.filter(status=AccountDeletionRequest.CONFIRMED)
    
    def rejected_requests(self):
        """
        Return all deletion requests with 'rejected' status.
        """
        return self.filter(status=AccountDeletionRequest.REJECTED)