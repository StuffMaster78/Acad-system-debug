
from django.apps import apps
from django.conf import settings

from django.db import models
from django.utils import timezone

from orders.models.requests import DraftRequest
from orders.order_enums import (
    OrderRequestStatus
)
from orders.models.orders import Order
from orders.models.websites import Website

User = settings.AUTH_USER_MODEL



class DraftFile(models.Model):
    """Files uploaded by writers in response to draft requests."""
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='draft_files'
    )
    draft_request = models.ForeignKey(
        DraftRequest,
        on_delete=models.CASCADE,
        related_name='files',
        help_text="The draft request this file fulfills"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='draft_files',
        help_text="The order this draft belongs to"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='draft_files_uploaded',
        help_text="Writer who uploaded the draft"
    )
    file = models.FileField(
        upload_to='draft_files/',
        help_text="The draft file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of what's in this draft"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the draft was uploaded"
    )
    is_visible_to_client = models.BooleanField(
        default=True,
        help_text="Whether client can view this draft"
    )

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['draft_request', 'uploaded_at']),
            models.Index(fields=['order', 'uploaded_at']),
        ]

    def __str__(self):
        return f"Draft File - {self.file_name} (Request #{self.draft_request.id})"

    def save(self, *args, **kwargs):
        # Auto-set website from order if not set
        if not self.website_id and self.order_id:
            self.website = self.order.website
        # Auto-set file_name from file if not set
        if self.file and not self.file_name:
            self.file_name = self.file.name.split('/')[-1]
        # Auto-set file_size from file if not set
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)