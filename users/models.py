from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
from django_countries.fields import CountryField # type: ignore
from rest_framework.exceptions import PermissionDenied
from phonenumber_field.modelfields import PhoneNumberField # type: ignore
from users.managers import CustomUserManager, ActiveManager
from .mixins import (
    RoleMixin,
    MFAMixin,
    NotificationPreferenceMixin,
    LoginSecurityMixin,
    ImpersonationMixin,
    DeletionMixin,
    DisciplineMixin,
    GeoDetectionMixin,
    TimestampMixin,
    SessionTrackingMixin,
    TrustedDeviceMixin,
    UserReferenceMixin,
    ApprovalMixin
)
# from websites.models import Website
from client_management.models import BlacklistedEmail
from notifications_system.models.notifications import Notification
from users.utils import logout_all_sessions
from django.apps import apps
from websites.models import Website
from notifications_system.models.notification_preferences import NotificationPreferenceProfile

# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()

class User(AbstractUser, PermissionsMixin, 
           RoleMixin, MFAMixin, NotificationPreferenceMixin, 
           LoginSecurityMixin, ImpersonationMixin,
           UserReferenceMixin, 
           DeletionMixin, DisciplineMixin, GeoDetectionMixin,
           TimestampMixin, SessionTrackingMixin, 
           TrustedDeviceMixin, ApprovalMixin):
    
    """
    Comprehensive/Central User model for managing writers, clients, and other roles.
    Includes impersonation, suspension, probation, and audit tracking.
    """
    email = models.EmailField(unique=True)
    notification_profile = models.ForeignKey(
        NotificationPreferenceProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    is_available = models.BooleanField(default=True)
    website = models.ForeignKey(
        'websites.Website',
        related_name='website_users',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()
    active_users = ActiveManager()

    # Compatibility shim: older code calls `_auto_detect_country_and_timezone`.
    # Our GeoDetectionMixin exposes `auto_detect_country(request)` instead.
    def _auto_detect_country_and_timezone(self, request=None):  # noqa: D401
        try:
            # Best effort; safe if content detection fails or no request provided
            self.auto_detect_country(request)
        except Exception:
            # Never block user creation on geo-detection
            pass

    # Backwards-compat: some tests expect `user.last_active` on the User model.
    @property
    def last_active(self):
        profile = getattr(self, 'user_main_profile', None)
        return getattr(profile, 'last_active', None) if profile else None

    @last_active.setter
    def last_active(self, value):
        # Ensure a profile exists
        profile = getattr(self, 'user_main_profile', None)
        if profile is None:
            from .models import UserProfile
            profile = UserProfile.objects.create(user=self, website=self.website)
        profile.last_active = value
        profile.save(update_fields=["last_active"])

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

    def place_on_probation(self, reason, duration_in_days=30):
        """
        Place the user on probation with a reason.
        """
        self.is_on_probation = True
        self.probation_reason = reason
        self.probation_start_date = now()
        self.probation_end_date = now() + timedelta(days=duration_in_days)
        self.save()

    def remove_from_probation(self):
        """
        Remove the user from probation.
        """
        self.is_on_probation = False
        self.probation_reason = None
        self.probation_start_date = None
        self.probation_end_date = None
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
        profile_update = self._get_role_profile()
        if profile_update:
            profile.update(profile_update)

        return profile
    
    def _get_role_profile(self):
        """Helper function to get role-based profile details."""
        profile_data = {}

        if self.is_client():
            profile_data.update({
                "loyalty_points": getattr(self.client_profile, 'loyalty_points', 0)
            })
        elif self.is_writer():
            writer_profile = getattr(self, 'writer_profile', None)
            profile_data.update({
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
            profile_data.update({
                "bio": getattr(editor_profile, 'bio', ""),
                "edited_orders": getattr(editor_profile, 'edited_orders', 0),
            })
        elif self.is_support():
            support_profile = getattr(self, 'support_profile', None)
            profile_data.update({
                "handled_tickets": getattr(support_profile, 'handled_tickets', 0),
                "resolved_orders": getattr(support_profile, 'resolved_orders', 0),
            })
        return profile_data

    def freeze_account(self):
        """
        Freeze the account, prevent login, log out active sessions,
        and schedule deletion in 90 days.
        """
        self.is_active = False  # Prevent login
        self.is_frozen = True
        self.is_deletion_requested = True
        self.deletion_requested_at = now()
        self.deletion_date = now() + timedelta(days=90)  # 3 months from now
        self.save()

        # Logout all active sessions
        logout_all_sessions(self)
    

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

    def archive_account(self):
        """
        Soft-delete and archive the account after 3 months.
        """
        self.is_archived = True
        self.is_frozen = False
        self.is_active = False
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


    def clean(self):
        """
        Custom validation for roles, website assignment, and status.
        """
        if self.is_global_role() and self.website:
            raise ValidationError(
                "Admins, Editors, and Support cannot be assigned to a website."
            )

        if self.is_suspended and self.is_available:
            raise ValidationError(
                "Suspended users cannot be marked as available."
            )

        if not self.profile_picture and not self.avatar:
            raise ValidationError(
                "Either an avatar or profile picture must be selected."
                )

        # Ensure writer does not exceed max orders
        if self.is_writer():
            writer_profile = getattr(
                self,
                'writer_profile',
                None
            )
            if writer_profile and hasattr(writer_profile, 'writer_level') and \
            writer_profile.writer_level:
                if writer_profile.active_orders > writer_profile.writer_level.max_orders:
                    raise ValidationError(
                        "Writer cannot exceed their maximum allowed active orders."
                    )

        if self.is_client() or self.is_writer():
            if not self.website:
                raise ValidationError(
                    "Clients and writers must be assigned to a website."
                )

        super().clean()



    def save(self, *args, **kwargs):
        """
        Assign a website dynamically based on request host, or fallback to the
        first active website.
        """
        if self.is_client() or self.is_writer():
            if not self.website:
                request = kwargs.pop('request', None)
                if request:
                    host = request.get_host().replace("www.", "")
                    self.website = Website.objects.filter(
                        domain=host, is_active=True
                    ).first() or Website.objects.filter(
                        domain__icontains=host, is_active=True
                    ).first() or Website.objects.filter(
                        is_active=True
                    ).first()

        # Auto-detect country if missing
        if not self.detected_country or not self.detected_timezone:
            self._auto_detect_country_and_timezone()

        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.username} ({self.role})"

class UserProfile(models.Model):
    """
    Stores profile information about the user.
    """
    AVATAR_CHOICES = (
        ('avatars/universal.png', 'Universal Avatar'),
        ('avatars/male1.png', 'Male Avatar 1'),
        ('avatars/male2.png', 'Male Avatar 2'),
        ('avatars/female1.png', 'Female Avatar 1'),
        ('avatars/female2.png', 'Female Avatar 2'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_main_profile'
    )
    preferences = models.JSONField(default=dict, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text=_("Upload a profile picture.")
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="websites_users_profiles",
        help_text=_("The website this user is associated with.")
    )
    avatar = models.CharField(
        max_length=255,
        choices=AVATAR_CHOICES,
        default='avatars/universal.png',
        help_text=_("Select a predefined avatar for privacy."),
        blank=False, # Ensuring avatar field is never blank
        null=True
    )
    # Country & State (Using django-countries for country selection)
    country = CountryField(
        blank=True,
        null=True,
        help_text=_("User-selected country")
    )
    state = models.CharField(
        max_length=100,
        null=True, blank=True,
        help_text=_("Manually entered state/province")
    )
    bio = models.TextField(
        null=True,
        blank=True,
        help_text=_("Optional bio field for writers/editors.")
    )
    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        help_text=_("Contact number for the user.")
    )

    is_deleted = models.BooleanField(default=False)
    deletion_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Last activity timestamp.")
    )

    def get_user_email(self):
        return self.user.email
    
    def get_user_role(self):
        return self.user.role

    def get_avatar_url(self):
        """Return the URL of the user's avatar."""
        if self.profile_picture:
            return self.profile_picture.url
        return self.avatar
    
    def get_profile(self):
        """
        Get the user's profile (returns None if not created).
        Optimized by using select_related to reduce DB hits.
        """
        try:
            return self.profile
        except UserProfile.DoesNotExist:
            return None

    def get_full_bio(self, max_length=200):
        """Return the user's bio with a maximum character length."""
        return self.bio[:max_length] + ('...' if len(self.bio) > max_length else '')
    
    def delete(self, using=None, soft_delete=False):
        """
        Deletes the user profile. If `soft_delete` is True, marks the profile
        as deleted instead of fully deleting it.
        """
        if soft_delete:
            self.is_deleted = True
            self.save()
        else:
            super().delete(using)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    

class UserAuditLog(models.Model):
    """
    Logs critical user actions for compliance, security, and auditing purposes.
    This includes sensitive actions such as account deletions, role changes, 
    failed login attempts, and other significant events.
    """
    
    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('EMAIL_CHANGE', 'Email Change'),
        ('ROLE_CHANGE', 'Role Change'),
        ('ACCOUNT_DELETION', 'Account Deletion'),
        ('FAILED_LOGIN', 'Failed Login Attempt'),
        ('SUSPENSION', 'Account Suspension'),
        ('ACTIVATION', 'Account Activation'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('BLACKLISTED', 'Email Blacklisted'),
        ('PHONE_NUMBER_CHANGE', 'Phone Number Change')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_audit_logs',
        help_text=_("The user whose action is being logged.")
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text=_("The website this audit log is associated with.")
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    admin_initiated = models.BooleanField(default=False)
    previous_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} at {self.timestamp}"

    class Meta:
        verbose_name = "User Audit Log"
        verbose_name_plural = "User Audit Logs"
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        # Automatically populate IP and user agent
        # if available (useful for security actions)
        if not self.ip_address:
            self.ip_address = 'Unknown IP'
        if not self.user_agent:
            self.user_agent = 'Unknown Agent'
        
        super().save(*args, **kwargs)


class ProfileUpdateRequest(models.Model):
    """
    Stores client or writer requests to update their profiles.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="update_requests_users"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="user_profile_update_requests"
    )
    requested_data = models.JSONField(
        help_text="Stores the fields requested for update."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_response = models.TextField(
        null=True,
        blank=True,
        help_text="Admin's response to the request."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def approve(self):
        """Apply the requested changes to the user's profile."""
        for field, value in self.requested_data.items():
            if hasattr(self.user, field):  # Ensure the field exists on the user model
                setattr(self.user, field, value)
            else:
                raise ValueError(f"Field {field} does not exist on user model.")
        self.user.save()
        self.status = "approved"
        self.save()

    def reject(self, reason):
        """Reject the request with a reason."""
        self.status = "rejected"
        self.admin_response = reason
        self.save()
class DeletionSettings(models.Model):
    """
    Model for managing the grace period before final deletion after a
    deletion request.
    """
    grace_period_days = models.PositiveIntegerField(
        default=30, 
        help_text="Global grace period in days before final deletion after a "
                  "deletion request."
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='deletion_settings',
        help_text=_("The website this deletion setting is associated with.")
)

    def __str__(self):
        return f"Grace period: {self.grace_period_days} days"


class UserActivity(models.Model):
    """
    Model for tracking user activities, including actions, timestamps, and
    additional details.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_activities',
        help_text=_("The user whose activity is being tracked.")
)
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='website_activities',
        help_text=_("The website where the activity took place.")
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"


class EmailVerification(models.Model):
    """
    Model to store email verification data, including the user, token, and
    expiration timestamp.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='user_email_verifications',
        help_text=_("The user whose email is being verified.")
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='email_verifications',
        help_text=_("The website this email verification is associated with.")
    )
    token = models.CharField(max_length=255)
    expiration = models.DateTimeField()

    def __str__(self):
        return f"Email verification for {self.user}"


class UserPermission(models.Model):
    """
    Model for managing user permissions, storing the permission name and
    granted timestamp.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_permissions_settings',
        help_text=_("The user this permission is associated with.")
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='wbsite_user_permissions',
        help_text=_("The website this user permission is associated with.")
    )
    permission_name = models.CharField(max_length=100)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} has {self.permission_name} permission"

class UserConsent(models.Model):
    """
    Model to track user consent, including whether consent is given, the
    consent date, and the consent type.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_consents',
        help_text=_("The user who has given consent.")
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='user_consents',
        help_text=_("The website this user consent is associated with.")
    )
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    consent_type = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user} consent for {self.consent_type}"