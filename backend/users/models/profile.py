from __future__ import annotations

from typing import cast

from django.core.exceptions import ValidationError
from django.db import models


def user_avatar_upload_path(instance: models.Model, filename: str) -> str:
    """
    Build the upload path for user profile avatars.
    """
    profile = cast("UserProfile", instance)
    user_pk = profile.user.pk if profile.user_id_safe is not None else "unknown"
    return f"users/avatars/{user_pk}/{filename}"


class UserProfile(models.Model):
    """
    Editable profile data for a user.

    This stores only approved, live profile data.
    Any requested edits that require review must go through
    ProfileUpdateRequest before being applied here.
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(
        max_length=150,
        blank=True,
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        null=True,
        blank=True,
    )
    # profile_url = 
    timezone = models.CharField(
        max_length=64,
        blank=True,
        default="Africa/Nairobi",
    )
    locale = models.CharField(
        max_length=32,
        blank=True,
        default="en",
    )
    country = models.CharField(
        max_length=64,
        blank=True,
    )
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last known activity timestamp for UI display.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user"]
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile<{self.user.email}>"

    @property
    def name_for_display(self) -> str:
        """
        Return the best available display label for the user.
        """
        return self.display_name or self.user.full_name or self.user.email

    @property
    def user_id_safe(self) -> int | None:
        """
        Return the related user's primary key in a type-checker-friendly way.
        """
        return self.user.pk


class ProfileUpdateRequestStatus(models.TextChoices):
    """
    Lifecycle states for profile update requests.
    """

    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    APPLIED = "applied", "Applied"
    CANCELLED = "cancelled", "Cancelled"


class ProfileUpdateRequest(models.Model):
    """
    Stores requested profile changes that must be reviewed before
    becoming live on UserProfile.
    """

    REVIEWABLE_FIELDS = {
        "display_name",
        "bio",
        "avatar",
        "timezone",
        "locale",
        "country",
    }

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile_update_requests",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="profile_update_requests",
    )
    profile = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="update_requests",
    )
    requested_changes = models.JSONField(
        default=dict,
        help_text="Requested profile field updates awaiting review.",
    )
    status = models.CharField(
        max_length=20,
        choices=ProfileUpdateRequestStatus.choices,
        default=ProfileUpdateRequestStatus.PENDING,
        db_index=True,
    )
    submitted_note = models.TextField(
        blank=True,
        help_text="Optional note from the user explaining the request.",
    )
    reviewed_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_profile_update_requests",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    review_note = models.TextField(
        blank=True,
        help_text="Internal review note or rejection explanation.",
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Profile Update Request"
        verbose_name_plural = "Profile Update Requests"

    def __str__(self) -> str:
        return (
            f"ProfileUpdateRequest<user={self.user.pk}, status={self.status}>"
        )

    def clean(self) -> None:
        """
        Validate that only allowed profile fields are being updated.
        """
        super().clean()

        if not isinstance(self.requested_changes, dict):
            raise ValidationError(
                {"requested_changes": "Requested changes must be an object."}
            )

        invalid_fields = (
            set(self.requested_changes.keys()) - self.REVIEWABLE_FIELDS
        )
        if invalid_fields:
            raise ValidationError(
                {
                    "requested_changes": (
                        "These fields are not allowed for profile update "
                        f"requests: {sorted(invalid_fields)}"
                    )
                }
            )

        if self.user.website is None:
            raise ValidationError(
                {"user": "User must belong to a website for this request."}
            )

        if self.user.website.pk != self.website.pk:
            raise ValidationError(
                {"website": "Website must match the user's website."}
            )

        if self.profile.user.pk != self.user.pk:
            raise ValidationError(
                {"profile": "Profile must belong to the same user."}
            )

    def can_be_reviewed(self) -> bool:
        """
        Return True if the request can move into review.
        """
        return self.status == ProfileUpdateRequestStatus.PENDING

    def can_be_approved(self) -> bool:
        """
        Return True if the request can be approved.
        """
        return self.status in {
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        }

    def can_be_rejected(self) -> bool:
        """
        Return True if the request can be rejected.
        """
        return self.status in {
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        }

    def can_be_applied(self) -> bool:
        """
        Return True if the approved request can be applied.
        """
        return self.status == ProfileUpdateRequestStatus.APPROVED