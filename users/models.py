from django.contrib.auth.models import AbstractUser
from .managers import ActiveManager
from core.models.base import WebsiteSpecificBaseModel
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(WebsiteSpecificBaseModel, AbstractUser):
    """
    Custom user model with roles for admin, editors, support, writers, and clients.
    Includes selectable avatars for privacy and specific profile methods.
    """
    objects = ActiveManager()

    ROLE_CHOICES = (
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
        help_text=_("Select a predefined avatar for privacy.")
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

    # Fields for writers
    verification_documents = models.JSONField(
        null=True,
        blank=True,
        help_text=_("Verification documents uploaded by the writer.")
    )
    rating = models.FloatField(
        default=0.0,
        help_text=_("Average rating for writers.")
    )
    completed_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Total completed orders by the writer.")
    )
    writer_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Level assigned to the writer.")
    )

    # Fields for editors
    edited_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Total orders edited by this editor.")
    )

    # Fields for support
    handled_tickets = models.PositiveIntegerField(
        default=0,
        help_text=_("Total tickets handled by support staff.")
    )
    resolved_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Total orders resolved by support staff.")
    )

    # Role-specific methods
    def is_client(self):
        """Check if the user is a client."""
        return self.role == 'client'

    def is_writer(self):
        """Check if the user is a writer."""
        return self.role == 'writer'

    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == 'admin'

    def is_editor(self):
        """Check if the user is an editor."""
        return self.role == 'editor'

    # Profile-specific methods
    def get_client_profile(self):
        """Get profile details for a client."""
        if not self.is_client():
            raise ValidationError(_("User is not a client."))
        return {
            "id": self.id,
            "email": self.email,
            "avatar": self.avatar,
            "phone_number": self.phone_number,
            "role": self.role,
        }

    def get_writer_profile(self):
        """Get profile details for a writer."""
        if not self.is_writer():
            raise ValidationError(_("User is not a writer."))
        return {
            "id": self.id,
            "email": self.email,
            "bio": self.bio,
            "writer_level": self.writer_level,
            "rating": self.rating,
            "completed_orders": self.completed_orders,
            "verification_documents": self.verification_documents,
        }

    def get_admin_profile(self):
        """Get profile details for an admin."""
        if not self.is_admin():
            raise ValidationError(_("User is not an admin."))
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role,
        }

    def get_editor_profile(self):
        """Get profile details for an editor."""
        if not self.is_editor():
            raise ValidationError(_("User is not an editor."))
        return {
            "id": self.id,
            "email": self.email,
            "bio": self.bio,
            "edited_orders": self.edited_orders,
        }

    def clean(self):
        """
        Add custom validation to enforce website assignment only for clients.
        """
        if self.role != 'client' and self.website is not None:
            raise ValidationError(_("Only clients can be associated with a website."))
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
        help_text=_("Maximum active orders allowed.")
    )
    min_orders = models.PositiveIntegerField(
        default=0,
        help_text=_("Minimum orders to qualify for this level.")
    )
    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        help_text=_("Minimum average rating to qualify for this level.")
    )

    def __str__(self):
        return f"{self.name} (Base Pay: ${self.base_pay_per_page}, Max Orders: {self.max_orders})"