from django.db import models
from django.utils.timezone import now, timedelta
from django.conf import settings
import hashlib, uuid, base64, json, random
from django.core.exceptions import PermissionDenied
from users.utils import get_client_ip
from cryptography.fernet import Fernet # type: ignore
# from django_otp.plugins.otp_totp.models import TOTPDevice
# from django_otp.oath import TOTP
from authentication.utils_backp import logout_all_sessions
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta
from django_countries.sfields import CountryField # type: ignore
import requests # type: ignore
from users.utils import get_client_ip
from rest_framework.exceptions import PermissionDenied

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session

from django.conf import settings
from django.core.mail import send_mail

# Generate a secret key for token encryption (Store this securely!)
SECRET_KEY = settings.SECRET_KEY[:32]
FERNET_KEY = base64.urlsafe_b64encode(SECRET_KEY.encode())

TOKEN_ENCRYPTION_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())

User = settings.AUTH_USER_MODEL




class User(AbstractUser, PermissionsMixin):
    """
    Comprehensive User model for managing writers, clients, and other roles.
    Includes impersonation, suspension, probation, and audit tracking.
    - Multi-Factor Authentication (MFA)
    - Role-based permissions
    - Session & security tracking
    """
    objects = CustomUserManager()
    active_users = ActiveManager() 
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('support', 'Support'),
        ('writer', 'Writer'),
        ('client', 'Client'),
    )
    MFA_METHODS = (
        ('none', 'No MFA'),
        ('email_otp', 'Email OTP'),
        ('sms_otp', 'SMS OTP'),
        ('totp', 'TOTP (Google Authenticator)'),
    )

    is_mfa_enabled = models.BooleanField(
        default=False,
        help_text="Is MFA enabled?"
    )
    mfa_method = models.CharField(
        max_length=20,
        choices=MFA_METHODS,
        default='none'
    )
    mfa_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Secret key for TOTP authentication."
    )
    backup_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Backup phone for SMS OTP"
    )
    backup_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Backup email for Email OTP"
    )
    otp_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="Temporary OTP Code"
    )
    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="OTP Expiry Time"
    )
    notify_mfa_login = models.BooleanField(
        default=True,
        help_text="Receive email alerts when logging in with MFA"
    )
    notify_password_change = models.BooleanField(
        default=True, help_text="Receive email alerts for password changes"
    )
    notify_wallet_transactions = models.BooleanField(
        default=True,
        help_text="Receive email alerts for wallet transactions"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts."
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last failed login."
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Indicates if the account is locked due to too many failed attempts."
    )
    lockout_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp until the account remains locked."
    )

    # General Fields
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        help_text=_("Role assigned to the user.")
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
    
    
    # Fields to manage account deletion
    is_frozen = models.BooleanField(
        default=False,
        help_text="Is the account frozen due to a deletion request?"
    )
    deletion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Scheduled date for account deletion."
    )
    is_blacklisted = models.BooleanField(
        default=False,
        help_text="Is the user's email blacklisted for the website?"
    )
    is_deletion_requested = models.BooleanField(
        default=False,
        help_text="Has the user requested account deletion?"
    )
    deletion_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the account deletion was requested."
    )

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
    suspension_start_date = models.DateTimeField(
        null=True,
        blank=True
    )
    suspension_end_date = models.DateTimeField(
        null=True,
        blank=True
    )
    probation_start_date = models.DateTimeField(
        null=True,
        blank=True
    )
    probation_end_date = models.DateTimeField(
        null=True,
        blank=True
    )


    mfa_recovery_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="One-time use token for MFA recovery."
    )
    mfa_recovery_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiry timestamp for MFA recovery token."
    )

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


    


    


    







    

