from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from .managers import ActiveManager
from core.models.base import WebsiteSpecificBaseModel


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

    # Writers-Specific Fields
    writer_level = models.ForeignKey(
        'WriterLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Level assigned to the writer.")
    )
    rating = models.FloatField(
        default=0.0,
        help_text=_("Average rating for writers.")
    )
    completed_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Total completed orders by the writer.")
    )
    number_of_takes = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of orders taken by the writer.")
    )
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_("Total earnings by the writer (USD).")
    )
    last_payment_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of the last payment to the writer.")
    )
    verification_status = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the writer has been verified.")
    )
    active_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of ongoing orders currently assigned to the writer.")
    )

    # Role-Specific Methods
    def is_client(self):
        return self.role == 'client'

    def is_writer(self):
        return self.role == 'writer'

    def is_admin(self):
        return self.role == 'admin'

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_editor(self):
        return self.role == 'editor'

    def is_support(self):
        return self.role == 'support'

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

class WriterLevel(models.Model):
    """
    Represents writer levels with constraints and pay details.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Name of the writer level.")
    )
    base_pay_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text=_("Base pay per page (USD).")
    )
    tip_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        help_text=_("Tip percentage for writers.")
    )
    max_orders = models.PositiveIntegerField(
        default=10,
        help_text=_("Maximum active orders allowed for writers at this level.")
    )
    min_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Minimum orders required to qualify for this level.")
    )
    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        help_text=_("Minimum average rating to qualify for this level.")
    )

    def __str__(self):
        return f"{self.name} (Base Pay: ${self.base_pay_per_page}, Max Orders: {self.max_orders})"


    def __str__(self):
        return f"{self.username} ({self.role})"