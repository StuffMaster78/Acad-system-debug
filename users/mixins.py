from django.db import models
from datetime import timedelta
from django.utils.timezone import now
import requests # type: ignore
from users.utils import get_client_ip
from django.utils import timezone
# from django.contrib.auth import get_user_model
# from users.models import User
from django.conf import settings


class UserReferenceMixin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="the_specific_user",
        help_text="Reference to the user associated with this model."
    )

    class Meta:
        abstract = True
class UserRole(models.TextChoices):
    """
    Enum-like class to represent user roles in the system.
    Each role corresponds to a specific permission set.
    """
    SUPERADMIN = 'superadmin', 'Super Admin'
    ADMIN = 'admin', 'Admin'
    EDITOR = 'editor', 'Editor'
    SUPPORT = 'support', 'Support'
    WRITER = 'writer', 'Writer'
    CLIENT = 'client', 'Client'
# 1. Role-Based Access Mixin
class RoleMixin(models.Model):
    """
    Mixin to add role-based access control to user models.
    Allows checking and managing roles and permissions for users.
    """

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT.value,
        help_text="Role assigned to the user."
    )

    class Meta:
        abstract = True

    def is_global_role(self):
        """
        Returns True if the user has a global role (superadmin, admin, 
        support, or editor).
        """
        return self.role in {
            UserRole.SUPERADMIN.value,
            UserRole.ADMIN.value,
            UserRole.SUPPORT.value,
            UserRole.EDITOR.value
        }

    def is_superadmin(self):
        return self.role == UserRole.SUPERADMIN.value

    def is_admin(self):
        return self.role == UserRole.ADMIN.value

    def is_support(self):
        return self.role == UserRole.SUPPORT.value

    def is_editor(self):
        return self.role == UserRole.EDITOR.value

    def is_writer(self):
        return self.role == UserRole.WRITER.value

    def is_client(self):
        return self.role == UserRole.CLIENT.value

    def is_staff_like(self):
        return self.role in {
            UserRole.SUPERADMIN.value,
            UserRole.ADMIN.value,
            UserRole.SUPPORT.value
        }

    def get_permissions(self):
        """
        Returns the list of permissions associated with the user's role.
        """
        permissions = {
            UserRole.SUPERADMIN.value: [
                'can_manage_users',
                'can_edit_content',
                'can_view_reports'
            ],
            UserRole.ADMIN.value: [
                'can_edit_content',
                'can_view_reports'
            ],
            UserRole.EDITOR.value: ['can_edit_content'],
            UserRole.SUPPORT.value: ['can_manage_support_tickets'],
            UserRole.WRITER.value: ['can_submit_work'],
            UserRole.CLIENT.value: ['can_view_orders']
        }
        return permissions.get(self.role, [])

    def has_permission(self, perm: str) -> bool:
        """
        Checks if the user has a specific permission.

        Args:
            perm (str): The permission to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        return perm in self.get_permissions()

# 2. MFA Mixin
class MFAMixin(models.Model):
    MFA_METHODS = (
        ('none', 'No MFA'),
        ('email_otp', 'Email OTP'),
        ('sms_otp', 'SMS OTP'),
        ('totp', 'TOTP (Google Authenticator)'),
        ('qr_code', 'QR CODE'),
    )

    is_mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(
        max_length=20,
        choices=MFA_METHODS,
        default='none'
    )
    mfa_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    # mfa_qr_code = models.ImageField(upload_to='mfa_qr_codes/', blank=True, null=True)
    backup_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    backup_email = models.EmailField(
        blank=True,
        null=True
    )
    otp_code = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )
    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True
    )

    mfa_recovery_token = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    mfa_recovery_expires = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        abstract = True


# 3. Notification Preferences Mixin
class NotificationPreferenceMixin(models.Model):
    notify_mfa_login = models.BooleanField(default=True)
    notify_password_change = models.BooleanField(default=True)
    notify_wallet_transactions = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_opt_in = models.BooleanField(default=False)
    mfa_recovery_token = models.CharField(max_length=64, blank=True, null=True)
    mfa_recovery_expires = models.DateTimeField(blank=True, null=True)
    class Meta:
        abstract = True


# 4. Login Security Mixin
class LoginSecurityMixin(models.Model):
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    lockout_until = models.DateTimeField(null=True, blank=True)
    events = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True


    def register_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= 5:  # configurable
            self.is_locked = True
            self.lockout_until = timezone.now() + timedelta(minutes=15)
        self.save()

    def is_currently_locked(self):
        if self.lockout_until and timezone.now() < self.lockout_until:
            return True
        if self.is_locked and (not self.lockout_until or timezone.now() >= self.lockout_until):
            self.is_locked = False
            self.failed_login_attempts = 0
            self.save()
            return False
        return self.is_locked

# 5. Impersonation Mixin
class ImpersonationMixin(models.Model):
    """
    Mixin to handle user impersonation by admins.
    Allows an admin to impersonate a user, and tracks who is impersonating whom.
    """
    is_impersonated = models.BooleanField(default=False)
    impersonated_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_impersonated_by",
        help_text="The admin user who is currently impersonating this user."
    )
    impersonation_start_at = models.DateTimeField(null=True, blank=True)
    impersonation_end_at = models.DateTimeField(null=True, blank=True)
    impersonation_reason = models.TextField(blank=True, null=True)


    class Meta:
        abstract = True

    def impersonate(self, admin):
        self.is_impersonated = True
        self.impersonated_by = admin
        self.save()

    def stop_impersonation(self):
        self.is_impersonated = False
        self.impersonated_by = None
        self.save()


# 6. Deletion Mixin
class DeletionMixin(models.Model):
    is_frozen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    is_deletion_requested = models.BooleanField(default=False)
    deletion_scheduled = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="deleted_%(class)s_set",
        on_delete=models.SET_NULL,
    )
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    grace_period_days = models.PositiveIntegerField(
        default=30, 
        help_text="Number of days before final deletion after request."
    )
    class Meta:
        abstract = True

    @property
    def deletion_status(self):
        """
        Returns a human-readable status of the account deletion process.
        """
        if self.deleted_at:
            return "deleted"
        if self.deletion_scheduled and timezone.now() >= self.deletion_scheduled:
            return "pending deletion"
        if self.deletion_scheduled:
            return "scheduled"
        if self.is_deletion_requested:
            return "requested"
        return "active"


    def request_deletion(self, delay_days=30):
        self.is_deletion_requested = True
        self.deletion_requested_at = timezone.now()
        self.deletion_scheduled = timezone.now() + timedelta(days=self.grace_period_days)
        self.is_frozen = True
        self.save()

    def cancel_deletion(self):
        self.is_deletion_requested = False
        self.deletion_requested_at = None
        self.deletion_scheduled = None
        self.is_frozen = False
        self.save()

    def force_delete_if_expired(self):
        """Force delete the user account if the grace period has expired."""
        if self.is_deletion_requested and self.deletion_scheduled:
            # Get grace period days (admin adjustable)
            grace_period_days = self.grace_period_days
            expiration_date = self.deletion_scheduled + timedelta(days=grace_period_days)
            
            # Check if the grace period has passed
            if timezone.now() >= expiration_date:
                # Perform soft deletion (mark as deleted, or freeze account)
                self.deleted_at = timezone.now()
                self.is_active = False
                self.is_frozen = True
                self.save()
                return True
        return False
    
    def soft_delete(self, force=False):
        """Set the user as inactive and timestamp the deletion."""
        if force or (self.deletion_scheduled and self.deletion_scheduled <= timezone.now()):
            self.is_active = False
            self.deleted_at = timezone.now()
            self.anonymize_user_data()
            self.save()

    def restore_account(self):
        """Undo deletion request if user changes their mind."""
        self.is_frozen = False
        self.is_deletion_requested = False
        self.deletion_scheduled = None
        self.deletion_requested_at = None
        self.deleted_at = None
        self.is_active = True
        self.save()

    def anonymize_user_data(self):
        """
        Scrub PII to protect user identity while keeping data structure intact.
        Override this in child classes to customize.
        """
        if hasattr(self, 'email'):
            self.email = f'anonymized+{self.pk}@example.com'
        if hasattr(self, 'username'):
            self.username = f'user_{self.pk}_deleted'
        if hasattr(self, 'first_name'):
            self.first_name = ''
        if hasattr(self, 'last_name'):
            self.last_name = ''
        if hasattr(self, 'phone_number'):
            self.phone_number = ''
        # Null any foreign keys (like profile_picture, website, etc.)
        if hasattr(self, 'profile_picture'):
            self.profile_picture = None
        if hasattr(self, 'bio'):
            self.bio = ''
        self.save()


# 7. Discipline Mixin (Suspension + Probation)
class DisciplineMixin(models.Model):
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)
    suspension_start_date = models.DateTimeField(null=True, blank=True)
    suspension_end_date = models.DateTimeField(null=True, blank=True)

    is_on_probation = models.BooleanField(default=False)
    probation_reason = models.TextField(blank=True, null=True)
    probation_start_date = models.DateTimeField(null=True, blank=True)
    probation_end_date = models.DateTimeField(null=True, blank=True)

    is_available = models.BooleanField(default=True)
    class Meta:
        abstract = True

    def suspend(self, reason, start_date=None, end_date=None):
        self.is_suspended = True
        self.suspension_reason = reason
        self.suspension_start_date = start_date or now()
        self.suspension_end_date = end_date
        self.save()

    def lift_suspension(self):
        self.is_suspended = False
        self.suspension_reason = None
        self.suspension_start_date = None
        self.suspension_end_date = None
        self.save()

    def place_on_probation(self, reason, duration_in_days=30):
        self.is_on_probation = True
        self.probation_reason = reason
        self.probation_start_date = now()
        self.probation_end_date = now() + timedelta(days=duration_in_days)
        self.save()

    def remove_from_probation(self):
        self.is_on_probation = False
        self.probation_reason = None
        self.probation_start_date = None
        self.probation_end_date = None
        self.save()


# 8. Geo Detection Mixin
class GeoDetectionMixin(models.Model):
    """Abstract mixin to automatically detect and store user's geographical information"""
    location = models.CharField(max_length=100, blank=True, null=True)
    detected_country = models.CharField(max_length=50, blank=True, null=True)
    detected_timezone = models.CharField(max_length=50, blank=True, null=True)
    detected_ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        abstract = True

    def auto_detect_country(self, request):
        if self.detected_country and self.detected_timezone:
            return
        
        ip_address = get_client_ip(request) if request else "8.8.8.8"
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=2)
            data = response.json()
            self.detected_country = data.get("country", "Unknown")
            self.detected_timezone = data.get("timezone", "Unknown")
            self.detected_ip = ip_address
        except requests.RequestException:
            self.detected_country = "Unknown"
            self.detected_timezone = "Unknown"


class SessionTrackingMixin(models.Model):
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    session_token = models.CharField(max_length=64, blank=True, null=True)
    session_expires_at = models.DateTimeField(null=True, blank=True)
    session_device = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        abstract = True

class TrustedDeviceMixin(models.Model):
    """Abstract mixin to manage trusted devices for a user."""
    trusted_devices = models.JSONField(default=list, blank=True)

    class Meta:
            abstract = True

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ApprovalMixin(models.Model):
    """Abstract mixin to handle approval workflows for user actions."""
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        related_name="approved_%(class)s_set",
        on_delete=models.SET_NULL,
    )
    rejected = models.BooleanField(default=False)
    rejected_reason = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class UserStampedMixin(models.Model):
    """
    Abstract base class that stamps created_by and updated_by fields.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_%(class)s_set",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True