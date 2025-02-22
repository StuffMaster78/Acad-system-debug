from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from .managers import ActiveManager
from django.utils.timezone import now, timedelta
from django_countries.fields import CountryField
import requests

class User(AbstractUser):
    """
    Comprehensive User model for managing writers, clients, and other roles.
    Includes impersonation, suspension, probation, and audit tracking.
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



    # # Role-Specific Profile Management
    # client_profile = models.OneToOneField('client_management.ClientProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile')
    # writer_profile = models.OneToOneField('writer_management.WriterProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='writer_profile')
    # editor_profile = models.OneToOneField('editor_management.EditorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='editor_profile')
    # support_profile = models.OneToOneField('support_management.SupportProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='support_profile')
    # admin_profile = models.OneToOneField('admin_management.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_profile') 
    # superadmin_profile = models.OneToOneField('superadmin_management.SuperadminProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='superadmin_profile') 


    # Role-Specific Methods
    def is_global_role(self):
        return self.role in ['superadmin', 'admin', 'support', 'editor']
    
    def is_client(self):
        return self.role == 'client'

    def is_writer(self):
        return self.role == 'writer'
    
    def is_support(self):
        return self.role == "support"
    
    def is_editor(self):
        return self.role == "editor"
    

    # Auto-detect Country & Timezone using `ipinfo.io`
    def auto_detect_country(self, ip_address):
        """
        Auto-detects the user's country and timezone using `ipinfo.io`.
        """
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json")
            data = response.json()
            self.detected_country = data.get("country", "")
            self.detected_timezone = data.get("timezone", "")
            self.detected_ip = ip_address
        except Exception:
            self.detected_country = "Unknown"
            self.detected_timezone = "Unknown"

    def save(self, *args, **kwargs):
        """ Auto-detect country & timezone if not set. """
        if not self.detected_country or not self.detected_timezone:
            ip_address = "8.8.8.8"  # Placeholder (replace with actual IP fetching logic)
            self.auto_detect_country(ip_address)

        super().save(*args, **kwargs)


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
        Freeze the account, mark deletion as requested, and schedule deletion 3 months from now.
        """
        self.is_active = False  # Prevent login
        self.is_frozen = True
        self.is_deletion_requested = True
        self.deletion_requested_at = now()
        self.deletion_date = now() + timedelta(days=90)  # 3 months from now
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
        from client_management.models import BlacklistedEmail

        BlacklistedEmail.objects.create(email=self.email, website=self.website)
        self.is_blacklisted = True
        self.save()

        # Whitelisting & Blacklisting Management
    def request_whitelisting(self):
        """ Sends an admin notification when a blacklisted user requests to be whitelisted. """
        if not self.is_blacklisted:
            return False  # User is not blacklisted
        from notifications_system.models import Notification
        Notification.objects.create(
            user=None,  # Notify all admins
            title="Whitelisting Request",
            message=f"User {self.username} ({self.email}) has requested to be whitelisted.",
            category="account"
        )
        return True

    def whitelist(self):
        """ Remove user from blacklist and notify them. """
        if not self.is_blacklisted:
            return False
        self.is_blacklisted = False
        self.is_whitelisted = True
        self.save()
        from notifications_system.models import Notification
        Notification.objects.create(
            user=self,
            title="Account Whitelisted",
            message="Your account has been successfully whitelisted. You can now access our services.",
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
        Add custom validation for roles, website assignment, and status.
        """
        if self.role != 'client' and self.website is not None:
            raise ValidationError(_("Only clients can be associated with a website."))

        if self.is_suspended and self.is_available:
            raise ValidationError(_("Suspended users cannot be marked as available."))
        
        if not self.profile_picture and not self.avatar:
            raise ValidationError(_("Either an avatar or profile picture must be selected."))

        # Ensure a writer does not exceed max orders
        if self.is_writer():
            writer_profile = getattr(self, 'writer_profile', None)
            if writer_profile and writer_profile.active_orders > writer_profile.writer_level.max_orders:
                raise ValidationError(_("Writer cannot exceed their maximum allowed active orders."))
        # Automatically fallback to the universal avatar if no profile picture is provided
        if not self.profile_picture and not self.avatar:
            self.avatar = 'avatars/universal.png'  # Fallback avatar

        super().clean()


    def save(self, *args, **kwargs):
        """
        Automatically fallback to a default avatar if no profile picture is provided.
        """
        if not self.profile_picture and not self.avatar:
            self.avatar = 'avatars/male1.png'  # Default fallback

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"