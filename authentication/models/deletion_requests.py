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
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    reason = models.TextField(null=True, blank=True)
    
    def confirm(self):
        self.status = self.CONFIRMED
        self.confirmation_time = timezone.now()
        self.save()
    
    def reject(self):
        self.status = self.REJECTED
        self.rejection_time = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Deletion request for {self.user.username} ({self.get_status_display()})"    


class DeletionRequestManager(models.Manager):
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