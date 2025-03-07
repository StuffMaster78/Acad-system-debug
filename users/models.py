from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta
from .managers import ActiveManager
from django_countries.fields import CountryField
import requests
from websites.models import Website 
from users.utils import get_client_ip
from rest_framework.exceptions import PermissionDenied
import uuid
import pyotp
import random
import hashlib
import base64
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import TOTP
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string


# Generate a secret key for token encryption (Store this securely!)
SECRET_KEY = settings.SECRET_KEY[:32]
FERNET_KEY = base64.urlsafe_b64encode(SECRET_KEY.encode())

TOKEN_ENCRYPTION_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
class User(AbstractUser):
    """
    Comprehensive User model for managing writers, clients, and other roles.
    Includes impersonation, suspension, probation, and audit tracking.
    - Multi-Factor Authentication (MFA)
    - Role-based permissions
    - Session & security tracking
    """
    objects = ActiveManager()

    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('support', 'Support'),
        ('writer', 'Writer'),
        ('client', 'Client'),
    )

    AVATAR_CHOICES = (
        ('avatars/universal.png', 'Universal Avatar'),
        ('avatars/male1.png', 'Male Avatar 1'),
        ('avatars/male2.png', 'Male Avatar 2'),
        ('avatars/female1.png', 'Female Avatar 1'),
        ('avatars/female2.png', 'Female Avatar 2'),
    )

    MFA_METHODS = (
        ('none', 'No MFA'),
        ('email_otp', 'Email OTP'),
        ('sms_otp', 'SMS OTP'),
        ('totp', 'TOTP (Google Authenticator)'),
    )

    is_mfa_enabled = models.BooleanField(default=False, help_text="Is MFA enabled?")
    mfa_method = models.CharField(max_length=20, choices=MFA_METHODS, default='none')
    mfa_secret = models.CharField(max_length=255, blank=True, null=True, help_text="Secret key for TOTP authentication.")
    backup_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Backup phone for SMS OTP")
    backup_email = models.EmailField(blank=True, null=True, help_text="Backup email for Email OTP")
    otp_code = models.CharField(max_length=6, blank=True, null=True, help_text="Temporary OTP Code")
    otp_expires_at = models.DateTimeField(blank=True, null=True, help_text="OTP Expiry Time")

    notify_mfa_login = models.BooleanField(default=True, help_text="Receive email alerts when logging in with MFA")
    notify_password_change = models.BooleanField(default=True, help_text="Receive email alerts for password changes")
    notify_wallet_transactions = models.BooleanField(default=True, help_text="Receive email alerts for wallet transactions")
    def generate_mfa_secret(self):
        """
        Generate and assign a new MFA secret key.
        """
        secret = pyotp.random_base32()
        self.mfa_secret = secret
        self.save()
        return secret
    
    def generate_totp_secret(self):
        """Generates a new TOTP secret key for Google Authenticator."""
        self.mfa_secret = pyotp.random_base32()
        self.save()
        return self.mfa_secret
    
    def generate_otp_code(self):
        """Generate OTP for TOTP or email authentication."""
        if self.mfa_method == 'totp':
            totp = TOTP(self.mfa_secret)
            return totp.generate_otp()
        elif self.mfa_method in ['sms', 'email']:
            return str(random.randint(100000, 999999))  # 6-digit OTP
        return None
    
    def get_totp_uri(self):
        """Returns the URI for configuring Google Authenticator."""
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(self.email, issuer_name="YourApp")
    
    def verify_totp(self, token):
        """Verifies a TOTP code."""
        return pyotp.TOTP(self.mfa_secret).verify(token)
    
    def generate_otp(self):
        """Generates a 6-digit OTP and sets an expiry time."""
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_expires_at = now() + timedelta(minutes=5)
        self.save()
        return self.otp_code

    def send_email_otp(self):
        """Sends OTP via email."""
        otp = self.generate_otp()
        send_mail(
            "Your MFA OTP Code",
            f"Use this OTP to log in: {otp}",
            "no-reply@yourapp.com",
            [self.email],
            fail_silently=False,
        )


    def generate_backup_codes(self):
        """
        Generates and stores backup codes for MFA recovery.
        """
        import random
        import string
        import hashlib
        codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(5)]
        hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]  # Hash each code
        self.backup_codes = hashed_codes
        self.save()
        return codes

    def use_backup_code(self, code):
        """
        Verify and remove a used backup code.
        """
        hashed_code = hashlib.sha256(code.encode()).hexdigest()
        if hashed_code in self.backup_codes:
            self.backup_codes.remove(hashed_code)
            self.save()
            return True
        return False
    
    def generate_email_otp(self):
        """Generates a 6-digit OTP for email authentication."""
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expires_at = now() + timedelta(minutes=5)
        self.save()
        return self.otp_code

    def verify_email_otp(self, otp):
        """Verifies Email OTP before expiration."""
        if self.otp_expires_at and now() > self.otp_expires_at:
            return False  # OTP Expired
        return self.otp_code == otp
    
    def verify_otp(self, otp):
        """Verifies OTP before expiration."""
        if self.otp_expires_at and now() > self.otp_expires_at:
            return False  # OTP Expired
        return self.otp_code == otp


    failed_login_attempts = models.IntegerField(default=0, help_text="Number of consecutive failed login attempts.")
    last_failed_login = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last failed login.")
    is_locked = models.BooleanField(default=False, help_text="Indicates if the account is locked due to too many failed attempts.")
    lockout_until = models.DateTimeField(null=True, blank=True, help_text="Timestamp until the account remains locked.")

    def lock_account(self, duration=15):
        """Locks the account for a given duration in minutes."""
        self.is_locked = True
        self.lockout_until = now() + timedelta(minutes=duration)
        self.save()

    def unlock_account(self):
        """Unlocks the account manually."""
        self.is_locked = False
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save()

    def check_if_locked(self):
        """Checks if the account should still be locked."""
        if self.is_locked and self.lockout_until and now() > self.lockout_until:
            self.unlock_account()  # Unlock automatically after lockout period
    # General Fields
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        help_text=_("Role assigned to the user.")
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text=_("Upload a profile picture.")
    )
    website = models.ForeignKey(
        Website, on_delete=models.SET_NULL, null=True, blank=True, related_name="users",
        help_text=_("The website this user is associated with.")
    )
    avatar = models.CharField(
        max_length=255,
        choices=AVATAR_CHOICES,
        default='avatars/universal.png',
        help_text=_("Select a predefined avatar for privacy."),
        blank=True,
        null=True
    )
    # Country & State (Using django-countries for country selection)
    country = CountryField(blank=True, null=True, help_text=_("User-selected country"))
    state = models.CharField(max_length=100, null=True, blank=True, help_text=_("Manually entered state/province"))
    bio = models.TextField(
        null=True,
        blank=True,
        help_text=_("Optional bio field for writers/editors.")
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text=_("Contact number for the user.")
    )
    is_available = models.BooleanField(
        default=True,
        help_text=_("Indicates whether the user is available for tasks.")
    ) 
    is_impersonated = models.BooleanField(
        default=False,
        help_text=_("Indicates whether this user is currently being impersonated.")
    )
    impersonated_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='impersonated_users',
        help_text=_("Admin currently impersonating this user.")
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(null=True, blank=True, help_text=_("Last activity timestamp."))
    
    # Fields to manage account deletion
    is_frozen = models.BooleanField(default=False, help_text="Is the account frozen due to a deletion request?")
    deletion_date = models.DateTimeField(null=True, blank=True, help_text="Scheduled date for account deletion.")
    is_blacklisted = models.BooleanField(default=False, help_text="Is the user's email blacklisted for the website?")
    is_deletion_requested = models.BooleanField(default=False, help_text="Has the user requested account deletion?")
    deletion_requested_at = models.DateTimeField(null=True, blank=True, help_text="When the account deletion was requested.")

    # Suspension and Probation Details
    is_suspended = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the user is suspended.")
    )
    is_on_probation = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the user is on probation.")
    )
    suspension_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Reason for suspension.")
    )
    probation_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Reason for probation.")
    )
    suspension_start_date = models.DateTimeField(null=True, blank=True)
    suspension_end_date = models.DateTimeField(null=True, blank=True)

    mfa_recovery_token = models.CharField(max_length=64, blank=True, null=True, help_text="One-time use token for MFA recovery.")
    mfa_recovery_expires = models.DateTimeField(null=True, blank=True, help_text="Expiry timestamp for MFA recovery token.")

    def generate_mfa_recovery_token(self):
        """
        Generate a one-time recovery token valid for 15 minutes.
        """
        self.mfa_recovery_token = get_random_string(64)
        self.mfa_recovery_expires = now() + timedelta(minutes=15)
        self.save()
        return self.mfa_recovery_token

    # # Role-Specific Profile Management
    # client_profile = models.OneToOneField('client_management.ClientProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile')
    # writer_profile = models.OneToOneField('writer_management.WriterProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='writer_profile')
    # editor_profile = models.OneToOneField('editor_management.EditorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='editor_profile')
    # support_profile = models.OneToOneField('support_management.SupportProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='support_profile')
    # admin_profile = models.OneToOneField('admin_management.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_profile') 
    # superadmin_profile = models.OneToOneField('superadmin_management.SuperadminProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='superadmin_profile') 

    email = models.EmailField(unique=True)  # Ensure email is unique for login
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Username is still required, but email is primary

    # Role-Specific Methods
    def is_global_role(self):
        return self.role in {'superadmin', 'admin', 'support', 'editor'}
    
    def is_client(self):
        return self.role == 'client'

    def is_writer(self):
        return self.role == 'writer'
    
    def is_support(self):
        return self.role == "support"
    
    def is_editor(self):
        return self.role == "editor"
    


    def auto_detect_country(self, request):
        """ Auto-detects the user's country and timezone only if not set. """
        if self.detected_country and self.detected_timezone:
            return  # Skip detection if already set
        
        ip_address = get_client_ip(request) if request else "8.8.8.8"  # Use real IP if available
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=2)
            data = response.json()
            self.detected_country = data.get("country", "Unknown")
            self.detected_timezone = data.get("timezone", "Unknown")
            self.detected_ip = ip_address
        except requests.RequestException:
            self.detected_country = "Unknown"
            self.detected_timezone = "Unknown"


    @property
    def display_avatar(self):
        """
        Returns the user's profile picture if available, otherwise the selected avatar.
        """
        if self.profile_picture:
            return self.profile_picture.url
        return f"/media/{self.avatar}"
    
    def suspend(self, reason, start_date=None, end_date=None):
        """
        Suspend a user with a reason and optional start and end dates.
        """
        self.is_suspended = True
        self.suspension_reason = reason
        self.suspension_start_date = start_date or now()
        self.suspension_end_date = end_date
        self.save()

    def lift_suspension(self):
        """
        Lift the suspension for the user.
        """
        self.is_suspended = False
        self.suspension_reason = None
        self.suspension_start_date = None
        self.suspension_end_date = None
        self.save()

    def place_on_probation(self, reason):
        """
        Place the user on probation with a reason.
        """
        self.is_on_probation = True
        self.probation_reason = reason
        self.save()

    def remove_from_probation(self):
        """
        Remove the user from probation.
        """
        self.is_on_probation = False
        self.probation_reason = None
        self.save()

    def impersonate(self, admin):
        """
        Mark this user as impersonated by the given admin.
        """
        self.is_impersonated = True
        self.impersonated_by = admin
        self.save()

    def stop_impersonation(self):
        """
        Stop impersonation of this user.
        """
        self.is_impersonated = False
        self.impersonated_by = None
        self.save()

    def get_profile(self):
        """
        Return structured profile details based on the user's role.
        """
        profile = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "phone_number": self.phone_number,
            "avatar": self.avatar,
            "is_suspended": self.is_suspended,
            "is_on_probation": self.is_on_probation,
            "date_joined": self.date_joined,
        }

        if self.is_client():
            profile.update({
                "loyalty_points": getattr(self.client_profile, 'loyalty_points', 0),
            })
        elif self.is_writer():
            writer_profile = getattr(self, 'writer_profile', None)
            profile.update({
                "bio": getattr(writer_profile, 'bio', ""),
                "writer_level": getattr(writer_profile, 'writer_level', None),
                "rating": getattr(writer_profile, 'rating', 0),
                "completed_orders": getattr(writer_profile, 'completed_orders', 0),
                "active_orders": getattr(writer_profile, 'active_orders', 0),
                "total_earnings": getattr(writer_profile, 'total_earnings', 0),
                "verification_status": getattr(writer_profile, 'verification_status', False),
            })
        elif self.is_editor():
            editor_profile = getattr(self, 'editor_profile', None)
            profile.update({
                "bio": getattr(editor_profile, 'bio', ""),
                "edited_orders": getattr(editor_profile, 'edited_orders', 0),
            })
        elif self.is_support():
            support_profile = getattr(self, 'support_profile', None)
            profile.update({
                "handled_tickets": getattr(support_profile, 'handled_tickets', 0),
                "resolved_orders": getattr(support_profile, 'resolved_orders', 0),
            })

        return profile
    

    def freeze_account(self):
        """
        Freeze the account, prevent login, log out active sessions, and schedule deletion in 90 days.
        """
        self.is_active = False  # Prevent login
        self.is_frozen = True
        self.is_deletion_requested = True
        self.deletion_requested_at = now()
        self.deletion_date = now() + timedelta(days=90)  # 3 months from now
        self.save()

        # Logout all active sessions
        sessions = Session.objects.filter(session_key=self.id)
        sessions.delete()
    
    def archive_account(self):
        """
        Soft-delete and archive the account after 3 months.
        """
        self.is_archived = True
        self.is_frozen = False
        self.is_active = False
        self.save()

    def reinstate_account(self):
        """
        Reinstate the account before deletion.
        """
        self.is_active = True
        self.is_frozen = False
        self.is_deletion_requested = False
        self.deletion_requested_at = None
        self.deletion_date = None
        self.save()

    def blacklist_account(self):
        """
        Blacklist the account email for the current website.
        """
        if not self.website:
            raise ValidationError(_("Cannot blacklist a user without an assigned website."))

        from client_management.models import BlacklistedEmail

        if not BlacklistedEmail.objects.filter(email=self.email, website=self.website).exists():
            BlacklistedEmail.objects.create(email=self.email, website=self.website)

        self.is_blacklisted = True
        self.save()


    def whitelist(self, admin_user):
        """ Remove user from blacklist, ensuring only superadmins can whitelist. """
        if not admin_user.is_superadmin:
            raise PermissionDenied(_("Only superadmins can whitelist users."))

        if not self.is_blacklisted:
            return False

        self.is_blacklisted = False
        self.save()
        from notifications_system.models import Notification
        Notification.objects.create(
            user=self,
            title="Account Whitelisted",
            message="Your account has been successfully whitelisted. You can now access our services.",
            category="account"
        )
        return True


    # Whitelisting & Blacklisting Management
    def request_whitelisting(self):
        """
        Sends a superadmin notification when a blacklisted user requests to be whitelisted.
        """
        if not self.is_blacklisted:
            return False  # User is not blacklisted

        from notifications_system.models import Notification
        from users.models import User  # Ensure import of the User model

        superadmins = User.objects.filter(role='superadmin')
        
        for admin in superadmins:
            Notification.objects.create(
                user=admin,
                title="Whitelisting Request",
                message=f"User {self.username} ({self.email}) has requested to be whitelisted.",
                category="account"
            )

        return True

        
    def place_on_probation(self, reason, duration_in_days=30):
        """Places the user on probation."""
        self.is_on_probation = True
        self.probation_reason = reason
        self.probation_start_date = now()
        self.probation_end_date = now() + timedelta(days=duration_in_days)
        self.save()

    def remove_from_probation(self):
        """Removes probation from the user."""
        self.is_on_probation = False
        self.probation_reason = None
        self.probation_start_date = None
        self.probation_end_date = None
        self.save()

    def clean(self):
        """
        Custom validation for roles, website assignment, and status.
        """
        if self.is_global_role() and self.website:
            raise ValidationError(_("Admins, Editors, and Support cannot be assigned to a website."))

        if self.is_suspended and self.is_available:
            raise ValidationError(_("Suspended users cannot be marked as available."))

        if not self.profile_picture and not self.avatar:
            raise ValidationError(_("Either an avatar or profile picture must be selected."))

        # Ensure writer does not exceed max orders
        if self.is_writer():
            writer_profile = getattr(self, 'writer_profile', None)
            if writer_profile and hasattr(writer_profile, 'writer_level') and writer_profile.writer_level:
                if writer_profile.active_orders > writer_profile.writer_level.max_orders:
                    raise ValidationError(_("Writer cannot exceed their maximum allowed active orders."))

        if self.is_client() or self.is_writer():
            if not self.website:
                raise ValidationError(_("Clients and writers must be assigned to a website."))

        super().clean()


    def save(self, *args, **kwargs):
        """
        Assign a website dynamically based on request host, or fallback to the first active website.
        Prioritizes exact domain match before falling back.
        """
        if self.is_client() or self.is_writer():
            if not self.website:
                request = kwargs.pop('request', None)
                if request:
                    host = request.get_host().replace("www.", "")
                    self.website = Website.objects.filter(domain=host, is_active=True).first() or \
                                Website.objects.filter(domain__icontains=host, is_active=True).first() or \
                                Website.objects.filter(is_active=True).first()
                if not self.website:
                    self.website = Website.objects.filter(is_active=True).first()  # Final fallback

        # Auto-detect country if missing
        if not self.detected_country or not self.detected_timezone:
            self.auto_detect_country(None)

        super().save(*args, **kwargs)




    def __str__(self):
        return f"{self.username} ({self.role})"
    
class ProfileUpdateRequest(models.Model):
    """
    Stores client or writer requests to update their profiles.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="update_requests")
    requested_data = models.JSONField(help_text="Stores the fields requested for update.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(null=True, blank=True, help_text="Admin's response to the request.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self):
        """Apply the requested changes to the user's profile."""
        for field, value in self.requested_data.items():
            setattr(self.user, field, value)
        self.user.save()
        self.status = "approved"
        self.save()

    def reject(self, reason):
        """Reject the request with a reason."""
        self.status = "rejected"
        self.admin_response = reason
        self.save()


class AccountDeletionRequest(models.Model):
    """
    Stores client or writer requests to delete their accounts.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deletion_requests")
    reason = models.TextField(help_text="Reason for requesting account deletion.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(null=True, blank=True, help_text="Admin's response to the request.")
    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        """Freeze the user account and schedule deletion."""
        self.user.freeze_account()
        self.status = "approved"
        self.save()

    def reject(self, reason):
        """Reject the deletion request with a reason."""
        self.status = "rejected"
        self.admin_response = reason
        self.save()

class UserSession(models.Model):
    """
    Tracks active user sessions for security monitoring.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=255, unique=True, help_text="Unique identifier for the session.")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the session.")
    device_type = models.CharField(max_length=255, null=True, blank=True, help_text="Device information for session tracking.")
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    expires_at = models.DateTimeField(help_text="When this session will expire.")
    is_active = models.BooleanField(default=True, help_text="Is the session currently active?")

    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.session_key} - {self.ip_address}"
    
    def is_expired(self):
        """Checks if the session is expired due to 24 hours of inactivity."""
        expired = self.last_activity < now() - timedelta(hours=24)
        if expired and self.is_active:
            self.is_active = False
            self.save()
        return expired

    
    def terminate(self):
        """Terminate the session."""
        from django.contrib.sessions.models import Session
        try:
            session = Session.objects.get(session_key=self.session_key)
            session.delete()
        except Session.DoesNotExist:
            pass

        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        """
        Prevents duplicate sessions by terminating any existing session
        before saving a new one.
        """
        UserSession.objects.update_or_create(
        session_key=self.session_key,
        defaults={"user": self.user, "ip_address": self.ip_address, "device_type": self.device_type},
        )
        super().save(*args, **kwargs)

    

class SecureToken(models.Model):
    """
    Stores API tokens securely using encryption.
    """
    TOKEN_PURPOSE_CHOICES = [
        ("api_key", "API Key"),
        ("refresh_token", "JWT Refresh Token"),
        ("other", "Other"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="tokens")
    encrypted_token = models.TextField(help_text="Encrypted API token.")
    purpose = models.CharField(max_length=20, choices=TOKEN_PURPOSE_CHOICES, help_text="Purpose of the token.")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this token will expire.")
    is_active = models.BooleanField(default=True, help_text="Is this token currently active?")

    def encrypt_token(self, raw_token):
        """Encrypts the token before saving."""
        cipher = Fernet(TOKEN_ENCRYPTION_KEY)
        encrypted = cipher.encrypt(raw_token.encode())
        return encrypted.decode()

    def decrypt_token(self):
        """Decrypts and returns the original token only if it's still active and not expired."""
        if not self.is_active or self.expires_at < now():
            raise PermissionDenied("This token is expired or revoked.")

        cipher = Fernet(TOKEN_ENCRYPTION_KEY)
        decrypted = cipher.decrypt(self.encrypted_token.encode())
        self.revoke() # Revoke the token after use to prevent replay attacks
        return decrypted.decode()


    def revoke(self):
        """Revokes the token."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - Active: {self.is_active}"
    

class SecureTokenManager(models.Manager):
    def create_encrypted_token(self, user, refresh_token):
        """Encrypts and stores the refresh token securely."""
        cipher = Fernet(FERNET_KEY)
        encrypted_token = cipher.encrypt(refresh_token.encode())

        return self.create(user=user, encrypted_token=encrypted_token.decode())

    def decrypt_token(self, encrypted_token):
        """Decrypts an encrypted refresh token."""
        cipher = Fernet(FERNET_KEY)
        return cipher.decrypt(encrypted_token.encode()).decode()

class EncryptedRefreshToken(models.Model):
    """Stores encrypted refresh tokens securely."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    encrypted_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SecureTokenManager()

    def __str__(self):
        return f"Token for {self.user.email}"
    

class AuditLog(models.Model):
    """
    Logs critical user actions including MFA changes.
    """
    ACTION_CHOICES = (
        ("MFA_ENABLED", "MFA Enabled"),
        ("MFA_DISABLED", "MFA Disabled"),
        ("MFA_RESET", "MFA Reset"),
        ("MFA_RECOVERY_REQUESTED", "MFA Recovery Requested"),
        ("MFA_RECOVERY_COMPLETED", "MFA Recovery Completed"),
        ("LOGIN_SUCCESS", "Login Successful"),
        ("LOGIN_FAILED", "Login Failed"),
        ("MFA_VERIFIED", "MFA Verified"),
        ("PASSWORD_RESET", "Password Reset"),
        ("ACCOUNT_UPDATED", "Account Updated"),
        ("ACCOUNT_LOCKED", "Account Locked"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
    
    def log_mfa_action(user, action, request):
        """
        Logs an MFA-related action with metadata.
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown') if request else "Unknown"

        AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent
        )

class TrustedDevice(models.Model):
    """
    Stores trusted devices for users who selected "Remember This Device" during MFA.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trusted_devices")
    device_token = models.CharField(max_length=255, unique=True, help_text="Hashed token for the trusted device.")
    device_info = models.TextField(help_text="Device user-agent or metadata for tracking.")
    last_used = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Expiration time for trusted device.")
    
    def is_valid(self):
        """Checks if the device is still trusted."""
        return self.expires_at > now()
    
    @staticmethod
    def generate_token():
        """Generates a secure hashed token."""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

class MagicLinkToken(models.Model):
    """
    Stores magic link login tokens with expiration.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="magic_links")
    token = models.UUIDField(default=uuid.uuid4, unique=True, help_text="Unique magic link token.")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Expiration time for the magic link.")

    def is_valid(self):
        """Checks if the magic link token is still valid."""
        if self.expires_at < now():
            from users.models import AuditLog
            AuditLog.objects.create(user=self.user, action="MAGIC_LINK_EXPIRED", ip_address="System")
            self.delete()  # Delete expired token
            return False
        return True


class BlockedIP(models.Model):
    """
    Stores blocked IPs for excessive failed login attempts.
    """
    ip_address = models.GenericIPAddressField(unique=True)
    blocked_until = models.DateTimeField(help_text="Time until this IP is blocked.")

    def is_blocked(self):
        """Checks if the IP is still blocked."""
        return self.blocked_until > now()