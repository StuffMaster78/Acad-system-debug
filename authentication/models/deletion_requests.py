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
        on_delete=models.CASCADE
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
        self.status = self.CONFIRMED
        self.confirmation_time = timezone.now()
        self.save()
    
    def reject(self):
        self.status = self.REJECTED
        self.rejection_time = timezone.now()
        self.save()

    def schedule_deletion(self, delay_hours=72):
        self.status = self.CONFIRMED
        self.confirmation_time = timezone.now()
        self.scheduled_deletion_time = self.confirmation_time + timezone.timedelta(hours=delay_hours)
        self.save()

    def generate_undo_token(self):
        import secrets
        self.undo_token = secrets.token_urlsafe(32)
        self.undo_token_expiry = timezone.now() + timezone.timedelta(hours=72)
        self.save()

    def perform_soft_delete(self):
        self.user.is_active = False
        self.user.save()
    
    def __str__(self):
        return f"Deletion request for {self.user.username} ({self.get_status_display()})"    


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