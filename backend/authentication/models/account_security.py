"""
Account Security Models
Handles account suspension, IP whitelisting, and email change verification.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class AccountSuspension(models.Model):
    """
    User-initiated account suspension for temporary account protection.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='account_suspension',
        help_text=_("User whose account is suspended")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='account_suspensions',
        help_text=_("Website context")
    )
    is_suspended = models.BooleanField(
        default=False,
        help_text=_("Whether account is currently suspended")
    )
    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When account was suspended")
    )
    suspension_reason = models.TextField(
        blank=True,
        help_text=_("Reason for suspension (user-provided)")
    )
    scheduled_reactivation = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Scheduled reactivation date (optional)")
    )
    reactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When account was reactivated")
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_suspended']),
            models.Index(fields=['website', 'is_suspended']),
            models.Index(fields=['scheduled_reactivation']),
        ]
        verbose_name = _("Account Suspension")
        verbose_name_plural = _("Account Suspensions")
    
    def suspend(self, reason="", scheduled_reactivation=None):
        """Suspend the account."""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.suspension_reason = reason
        self.scheduled_reactivation = scheduled_reactivation
        self.reactivated_at = None
        self.save()
        
        # Deactivate user account
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
    
    def reactivate(self):
        """Reactivate the account."""
        self.is_suspended = False
        self.reactivated_at = timezone.now()
        self.save()
        
        # Reactivate user account
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])
    
    def check_scheduled_reactivation(self):
        """Check if scheduled reactivation time has passed."""
        if self.scheduled_reactivation and timezone.now() >= self.scheduled_reactivation:
            self.reactivate()
            return True
        return False
    
    def __str__(self):
        status = "Suspended" if self.is_suspended else "Active"
        return f"Account suspension for {self.user.email} - {status}"


class IPWhitelist(models.Model):
    """
    User-controlled IP whitelist for restricting logins to trusted IPs.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_entries',
        help_text=_("User who owns this whitelist entry")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_entries',
        help_text=_("Website context")
    )
    ip_address = models.GenericIPAddressField(
        help_text=_("Whitelisted IP address")
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("User-friendly label (e.g., 'Home', 'Office')")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this IP was whitelisted")
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this IP was last used for login")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this whitelist entry is active")
    )
    
    class Meta:
        unique_together = ['user', 'website', 'ip_address']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['website', 'user']),
            models.Index(fields=['ip_address']),
        ]
        verbose_name = _("IP Whitelist Entry")
        verbose_name_plural = _("IP Whitelist Entries")
    
    def __str__(self):
        label = f" ({self.label})" if self.label else ""
        return f"IP whitelist for {self.user.email}: {self.ip_address}{label}"


class UserIPWhitelistSettings(models.Model):
    """
    Settings for user's IP whitelist feature.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_settings',
        help_text=_("User whose whitelist settings are configured")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_settings',
        help_text=_("Website context")
    )
    is_enabled = models.BooleanField(
        default=False,
        help_text=_("Whether IP whitelist is enabled for this user")
    )
    allow_emergency_bypass = models.BooleanField(
        default=True,
        help_text=_("Allow emergency bypass via email verification")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_enabled']),
            models.Index(fields=['website', 'user']),
        ]
        verbose_name = _("IP Whitelist Settings")
        verbose_name_plural = _("IP Whitelist Settings")
    
    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"IP whitelist settings for {self.user.email} - {status}"


class EmailChangeRequest(models.Model):
    """
    Tracks email change requests with verification and admin approval.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('admin_approved', 'Admin Approved'),
        ('email_verified', 'Email Verified'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
        help_text=_("User requesting email change")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
        help_text=_("Website context")
    )
    old_email = models.EmailField(
        help_text=_("Current email address")
    )
    new_email = models.EmailField(
        help_text=_("New email address to change to")
    )
    verification_token = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Token for verifying new email")
    )
    old_email_verification_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Token for confirming old email")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Current status of the email change request")
    )
    verified = models.BooleanField(
        default=False,
        help_text=_("Whether new email has been verified")
    )
    old_email_confirmed = models.BooleanField(
        default=False,
        help_text=_("Whether old email change was confirmed")
    )
    admin_approved = models.BooleanField(
        default=False,
        help_text=_("Whether admin has approved the email change")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_email_changes',
        help_text=_("Admin who approved the email change")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When admin approved the email change")
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text=_("Reason for rejection if rejected")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When change was requested")
    )
    expires_at = models.DateTimeField(
        help_text=_("When this request expires")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When email change was completed")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['website', 'user']),
            models.Index(fields=['verification_token']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = _("Email Change Request")
        verbose_name_plural = _("Email Change Requests")
    
    @property
    def is_expired(self):
        """Check if request has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if request is valid and not expired."""
        return (
            not self.is_expired 
            and self.status in ['pending', 'admin_approved', 'email_verified']
            and not self.verified
        )
    
    @property
    def requires_admin_approval(self):
        """Check if request requires admin approval."""
        return self.status == 'pending' and not self.admin_approved
    
    @property
    def requires_email_verification(self):
        """Check if request requires email verification."""
        return self.admin_approved and not self.verified
    
    def __str__(self):
        status = "Verified" if self.verified else "Pending"
        return f"Email change: {self.old_email} → {self.new_email} ({status})"


class PhoneVerification(models.Model):
    """
    Tracks phone number verification for users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        help_text=_("User whose phone is being verified")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        help_text=_("Website context")
    )
    phone_number = models.CharField(
        max_length=20,
        help_text=_("Phone number to verify (E.164 format)")
    )
    verification_code = models.CharField(
        max_length=6,
        help_text=_("6-digit verification code")
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Whether phone number is verified")
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When phone was verified")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When verification was initiated")
    )
    expires_at = models.DateTimeField(
        help_text=_("When verification code expires")
    )
    attempts = models.IntegerField(
        default=0,
        help_text=_("Number of verification attempts")
    )
    max_attempts = models.IntegerField(
        default=3,
        help_text=_("Maximum verification attempts allowed")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['website', 'user']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = _("Phone Verification")
        verbose_name_plural = _("Phone Verifications")
    
    @property
    def is_expired(self):
        """Check if verification code has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_exhausted(self):
        """Check if verification attempts are exhausted."""
        return self.attempts >= self.max_attempts
    
    def __str__(self):
        status = "Verified" if self.is_verified else "Pending"
        return f"Phone verification for {self.user.email}: {self.phone_number} ({status})"

