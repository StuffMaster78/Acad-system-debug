"""
Privacy Settings Models
Handles privacy settings for writers and clients.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class WriterPrivacySettings(models.Model):
    """
    Privacy settings for writers - controls what clients can see.
    System sets defaults - writers cannot change these directly.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='writer_privacy_settings',
        help_text=_("Writer whose privacy settings are configured")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_privacy_settings',
        help_text=_("Website context")
    )
    # What clients see
    show_writer_id = models.BooleanField(
        default=True,
        help_text=_("Clients see Writer ID")
    )
    show_pen_name = models.BooleanField(
        default=True,
        help_text=_("Clients see Pen Name (if set)")
    )
    show_completed_orders_count = models.BooleanField(
        default=True,
        help_text=_("Clients see number of completed orders")
    )
    show_rating = models.BooleanField(
        default=True,
        help_text=_("Clients see writer rating")
    )
    show_workload = models.BooleanField(
        default=True,
        help_text=_("Clients see current workload")
    )
    show_bio = models.BooleanField(
        default=False,
        help_text=_("Clients see bio (admin-controlled)")
    )
    show_avatar = models.BooleanField(
        default=True,
        help_text=_("Clients see avatar (if approved)")
    )
    # Admin controls
    bio_approved = models.BooleanField(
        default=False,
        help_text=_("Whether bio is approved by admin")
    )
    bio_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bios',
        help_text=_("Admin who approved the bio")
    )
    bio_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When bio was approved")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'website']),
        ]
        verbose_name = _("Writer Privacy Settings")
        verbose_name_plural = _("Writer Privacy Settings")
    
    def __str__(self):
        return f"Privacy settings for {self.user.email}"


class ClientPrivacySettings(models.Model):
    """
    Privacy settings for clients - controls what writers can see.
    System sets defaults - clients cannot change these directly.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_privacy_settings',
        help_text=_("Client whose privacy settings are configured")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='client_privacy_settings',
        help_text=_("Website context")
    )
    # What writers see
    show_client_id = models.BooleanField(
        default=True,
        help_text=_("Writers see Client ID")
    )
    show_pen_name = models.BooleanField(
        default=True,
        help_text=_("Writers see Pen Name (if set)")
    )
    show_real_name = models.BooleanField(
        default=False,
        help_text=_("Writers see real name (admin-controlled)")
    )
    show_email = models.BooleanField(
        default=False,
        help_text=_("Writers see email (admin-controlled)")
    )
    show_avatar = models.BooleanField(
        default=True,
        help_text=_("Writers see avatar")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'website']),
        ]
        verbose_name = _("Client Privacy Settings")
        verbose_name_plural = _("Client Privacy Settings")
    
    def __str__(self):
        return f"Privacy settings for {self.user.email}"


class PenName(models.Model):
    """
    Pen names for users (writers and clients can have pen names).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pen_names',
        help_text=_("User who owns this pen name")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='pen_names',
        help_text=_("Website context")
    )
    pen_name = models.CharField(
        max_length=100,
        help_text=_("The pen name")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this is the active pen name")
    )
    is_approved = models.BooleanField(
        default=False,
        help_text=_("Whether pen name is approved by admin (for writers)")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_pen_names',
        help_text=_("Admin who approved the pen name")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When pen name was approved")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'website', 'pen_name']
        indexes = [
            models.Index(fields=['user', 'website', 'is_active']),
            models.Index(fields=['pen_name']),
        ]
        verbose_name = _("Pen Name")
        verbose_name_plural = _("Pen Names")
    
    def __str__(self):
        return f"{self.pen_name} ({self.user.email})"

