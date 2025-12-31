from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.contrib.auth import get_user_model
User = get_user_model()


class WriterSupportTicket(models.Model):
    """
    Writers can submit tickets for support.
    """
    CATEGORY_CHOICES = [
        ("Order Issue", "Order Issue"),
        ("Payment Issue", "Payment Issue"),
        ("Technical Support", "Technical Support"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="support_tickets"
    )
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES
    )
    description = models.TextField(
        help_text="Details of the issue."
    )
    attachment = models.FileField(
        upload_to="writer_tickets/",
        blank=True, null=True,
        help_text="Optional attachment."
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="Open"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="resolved_writer_tickets"
    )

    def __str__(self):
        return f"Ticket {self.id} - {self.writer.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['writer', 'status', 'created_at']),
            models.Index(fields=['website', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['writer', 'status']),
        ]

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None) and getattr(self, 'writer', None):
            try:
                self.website_id = self.writer.website_id
            except Exception:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Writer Support Ticket"
        verbose_name_plural = "Writer Support Tickets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['writer', 'status', 'created_at']),
            models.Index(fields=['website', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['resolved_by', 'status']),
        ]