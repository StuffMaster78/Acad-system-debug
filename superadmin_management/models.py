from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

User = settings.AUTH_USER_MODEL 


class SuperadminProfile(models.Model):
    """
    Profile for Superadmins. Grants full system control.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="superadmin_profile")

    # Superadmin Permissions
    can_manage_users = models.BooleanField(default=True, help_text="Can add/edit/suspend/delete users.")
    can_manage_payments = models.BooleanField(default=True, help_text="Can oversee all payments.")
    can_view_reports = models.BooleanField(default=True, help_text="Can view financial and operational reports.")
    can_modify_settings = models.BooleanField(default=True, help_text="Can modify system-wide settings.")
    can_promote_users = models.BooleanField(default=True, help_text="Can promote/demote users.")
    can_suspend_users = models.BooleanField(default=True, help_text="Can suspend or reactivate users.")
    can_blacklist_users = models.BooleanField(default=True, help_text="Can blacklist and unblacklist users.")
    can_resolve_disputes = models.BooleanField(default=True, help_text="Can resolve order disputes.")
    can_override_payments = models.BooleanField(default=True, help_text="Can manually adjust payments.")
    can_track_admins = models.BooleanField(default=True, help_text="Can track all admin actions.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_permission(self, perm):
        """Check if an admin has a specific permission."""
        return getattr(self, perm, False)

    def __str__(self):
        return f"Superadmin Profile - {self.user.username}"

    class Meta:
        verbose_name = "Superadmin Profile"
        verbose_name_plural = "Superadmin Profiles"


class Probation(models.Model):
    """
    Tracks users placed on probation by a superadmin.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="probation_records")
    placed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="probation_placed"
    )
    reason = models.TextField(help_text="Reason for probation.")
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the probation is still active."
    )

    def check_expiry(self):
        """ Automatically deactivate probation if end_date has passed. """
        if self.end_date < now():
            self.is_active = False
            self.save()

    def __str__(self):
        return f"{self.user.username} on probation until {self.end_date}"

    class Meta:
        verbose_name = "Probation Record"
        verbose_name_plural = "Probation Records"


class Blacklist(models.Model):
    """
    Tracks blacklisted users, emails, or IPs.
    """
    BLACKLIST_TYPE_CHOICES = [
        ('user', 'User Account'),
        ('email', 'Email Address'),
        ('ip', 'IP Address'),
    ]

    blacklist_type = models.CharField(
        max_length=10,
        choices=BLACKLIST_TYPE_CHOICES,
        default='user'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_record"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Blacklisted email (if applicable)."
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="Blacklisted IP (if applicable)."
    )
    reason = models.TextField(
        help_text="Reason for blacklisting."
    )
    blacklisted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_placed"
    )
    date_blacklisted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the blacklist is still active."
    )

    def __str__(self):
        if self.user:
            return f"Blacklisted User: {self.user.username} ({self.reason})"
        elif self.email:
            return f"Blacklisted Email: {self.email} ({self.reason})"
        elif self.ip_address:
            return f"Blacklisted IP: {self.ip_address} ({self.reason})"
        return "Unknown Blacklist Entry"

    class Meta:
        verbose_name = "Blacklist Record"
        verbose_name_plural = "Blacklist Records"


class SuperadminLog(models.Model):
    """
    Logs actions performed by Superadmins for security tracking.
    """
    ACTION_TYPES = [
        ('user_manage', 'User Management'),
        ('payment', 'Payment Override'),
        ('report_access', 'Report Access'),
        ('settings_change', 'Settings Modification'),
        ('promotion', 'User Promotion/Demotion'),
        ('suspension', 'User Suspension'),
        ('probation', 'User Probation'),
        ('blacklist', 'User Blacklisting'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('admin_tracking', 'Admin Tracking'),
        ('override', 'System Override'),
    ]

    superadmin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="superadmin_logs"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default='override'
    )
    action = models.CharField(max_length=255)
    action_details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.superadmin.username} - {self.get_action_type_display()} - {self.timestamp}"

    class Meta:
        verbose_name = "Superadmin Log"
        verbose_name_plural = "Superadmin Logs"
        ordering = ['-timestamp']

class Appeal(models.Model):
    """Users can request a review of their probation or blacklist status."""
    APPEAL_TYPE_CHOICES = [
        ('probation', 'Probation'),
        ('blacklist', 'Blacklist'),
        ('suspension', 'Suspension'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appeals"
    )
    appeal_type = models.CharField(
        max_length=10,
        choices=APPEAL_TYPE_CHOICES
    )
    reason = models.TextField(
        help_text="Why should this decision be reconsidered?"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appeal_reviews"
    )
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.appeal_type} - {self.status}"
    

class UserActionLog(models.Model):
    """Logs key actions taken on users by Superadmins."""
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="user_action_logs"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="target_user"
    )
    action = models.CharField(max_length=50)  # e.g., "Suspended", "Reactivated", "Role Changed"
    details = models.TextField(blank=True, null=True)  # Optional extra details
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.target_user.username} ({self.timestamp})"