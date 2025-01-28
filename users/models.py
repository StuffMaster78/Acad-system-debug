from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from .managers import ActiveManager
from core.models.base import WebsiteSpecificBaseModel
from django.utils.timezone import now, timedelta

class User(WebsiteSpecificBaseModel, AbstractUser):
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
        ('avatars/male1.png', _('Male Avatar 1')),
        ('avatars/male2.png', _('Male Avatar 2')),
        ('avatars/female1.png', _('Female Avatar 1')),
        ('avatars/female2.png', _('Female Avatar 2')),
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
        default='avatars/male1.png',
        help_text=_("Select a predefined avatar for privacy."),
        blank=True,
        null=True
    )
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
    is_suspended = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the user is suspended.")
    )
    is_on_probation = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the user is on probation.")
    )
    is_impersonated = models.BooleanField(
        default=False,
        help_text=_("Indicates whether this user is currently being impersonated.")
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(null=True, blank=True, help_text=_("Last activity timestamp."))
    impersonated_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='impersonated_users',
        help_text=_("Admin currently impersonating this user.")
    )


    # Fields to manage account deletion
    is_frozen = models.BooleanField(default=False, help_text="Is the account frozen due to a deletion request?")
    deletion_date = models.DateTimeField(null=True, blank=True, help_text="Scheduled date for account deletion.")
    is_blacklisted = models.BooleanField(default=False, help_text="Is the user's email blacklisted for the website?")
    is_deletion_requested = models.BooleanField(default=False, help_text="Has the user requested account deletion?")
    deletion_requested_at = models.DateTimeField(null=True, blank=True, help_text="When the account deletion was requested.")

    # Suspension and Probation Details
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

    # Role-Specific Methods
    def is_global_role(self):
        return self.role in ['superadmin', 'admin', 'support']
    
    def is_client(self):
        return self.role == 'client'

    def is_writer(self):
        return self.role == 'writer'

    

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

        if self.is_writer():
            profile.update({
                "bio": self.bio,
                "writer_level": self.writer_level.name if self.writer_level else None,
                "rating": self.rating,
                "completed_orders": self.completed_orders,
                "active_orders": self.active_orders,
                "total_earnings": self.total_earnings,
                "last_payment_date": self.last_payment_date,
                "verification_status": self.verification_status,
            })
        elif self.is_editor():
            profile.update({
                "bio": self.bio,
                "edited_orders": self.edited_orders,
            })
        elif self.is_support():
            profile.update({
                "handled_tickets": self.handled_tickets,
                "resolved_orders": self.resolved_orders,
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

    def clean(self):
        """
        Add custom validation for roles, website assignment, and status.
        """
        if self.role != 'client' and self.website is not None:
            raise ValidationError(_("Only clients can be associated with a website."))

        if self.is_suspended and self.is_available:
            raise ValidationError(_("Suspended users cannot be marked as available."))

        if self.is_writer() and self.active_orders > self.writer_level.max_orders:
            raise ValidationError(_("Writer cannot exceed their maximum allowed active orders."))

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