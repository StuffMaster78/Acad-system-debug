"""
Password Security Models
Handles password history, expiration, and breach detection.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class PasswordHistory(models.Model):
    """
    Stores password history to prevent reuse of recent passwords.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_history',
        help_text=_("User whose password history is tracked")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='password_histories',
        help_text=_("Website context for multi-tenancy")
    )
    password_hash = models.CharField(
        max_length=255,
        help_text=_("Hashed password (stored securely)")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this password was set")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['website', 'user']),
        ]
        verbose_name = _("Password History")
        verbose_name_plural = _("Password Histories")
    
    def __str__(self):
        return f"Password history for {self.user.email} at {self.created_at}"


class PasswordExpirationPolicy(models.Model):
    """
    Tracks password expiration for users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_expiration_policy',
        help_text=_("User whose password expiration is tracked")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='password_expiration_policies',
        help_text=_("Website context")
    )
    password_changed_at = models.DateTimeField(
        default=timezone.now,
        help_text=_("When the password was last changed")
    )
    expires_in_days = models.IntegerField(
        default=90,
        help_text=_("Number of days before password expires")
    )
    warning_days_before = models.IntegerField(
        default=7,
        help_text=_("Days before expiration to show warning")
    )
    is_exempt = models.BooleanField(
        default=False,
        help_text=_("If True, password never expires")
    )
    last_warning_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the last expiration warning was sent")
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'password_changed_at']),
            models.Index(fields=['website', 'user']),
        ]
        verbose_name = _("Password Expiration Policy")
        verbose_name_plural = _("Password Expiration Policies")
    
    @property
    def expires_at(self):
        """Calculate when password expires."""
        if self.is_exempt:
            return None
        return self.password_changed_at + timezone.timedelta(days=self.expires_in_days)
    
    @property
    def is_expired(self):
        """Check if password is expired."""
        if self.is_exempt:
            return False
        expires_at = self.expires_at
        return expires_at and expires_at < timezone.now()
    
    @property
    def is_expiring_soon(self):
        """Check if password is expiring soon."""
        if self.is_exempt or self.is_expired:
            return False
        expires_at = self.expires_at
        if not expires_at:
            return False
        warning_date = expires_at - timezone.timedelta(days=self.warning_days_before)
        return timezone.now() >= warning_date
    
    @property
    def days_until_expiration(self):
        """Get days until password expires."""
        if self.is_exempt:
            return None
        expires_at = self.expires_at
        if not expires_at:
            return None
        if self.is_expired:
            return 0
        delta = expires_at - timezone.now()
        return max(0, delta.days)
    
    def update_password_changed(self):
        """Update password changed timestamp."""
        self.password_changed_at = timezone.now()
        self.last_warning_sent = None
        self.save(update_fields=['password_changed_at', 'last_warning_sent'])
    
    def __str__(self):
        status = "exempt" if self.is_exempt else f"expires in {self.days_until_expiration} days"
        return f"Password policy for {self.user.email} - {status}"


class PasswordBreachCheck(models.Model):
    """
    Tracks password breach checks and results.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_breach_checks',
        help_text=_("User whose password was checked")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='password_breach_checks',
        help_text=_("Website context")
    )
    password_hash_prefix = models.CharField(
        max_length=5,
        help_text=_("First 5 characters of SHA-1 hash (for HIBP API)")
    )
    is_breached = models.BooleanField(
        default=False,
        help_text=_("Whether password was found in breach database")
    )
    breach_count = models.IntegerField(
        default=0,
        help_text=_("Number of times password appeared in breaches")
    )
    checked_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the check was performed")
    )
    action_taken = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No Action'),
            ('warned', 'User Warned'),
            ('forced_change', 'Password Change Forced'),
        ],
        default='none',
        help_text=_("Action taken based on breach check")
    )
    
    class Meta:
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['user', '-checked_at']),
            models.Index(fields=['website', 'user']),
            models.Index(fields=['is_breached', 'action_taken']),
        ]
        verbose_name = _("Password Breach Check")
        verbose_name_plural = _("Password Breach Checks")
    
    def __str__(self):
        status = "BREACHED" if self.is_breached else "SAFE"
        return f"Breach check for {self.user.email} - {status}"

