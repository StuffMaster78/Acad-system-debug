from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from class_management.constants import (
    ClassAccessGrantStatus,
    TwoFactorRequestStatus,
)


class ClassAccessDetail(models.Model):
    """
    Protected portal access information for a class order.

    Credentials should be encrypted before being stored. This model should
    only be read through access services so audit logs are always created.
    """

    class_order = models.OneToOneField(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="access_detail",
    )

    institution_name = models.CharField(max_length=255, blank=True)
    institution_state = models.CharField(max_length=120, blank=True)
    class_portal_url = models.URLField(max_length=500, blank=True)

    class_name = models.CharField(max_length=255, blank=True)
    class_code = models.CharField(max_length=120, blank=True)

    login_username = models.CharField(max_length=255, blank=True)
    login_password_encrypted = models.TextField(blank=True)

    requires_two_factor = models.BooleanField(default=False)
    two_factor_method = models.CharField(max_length=120, blank=True)

    preferred_contact_method = models.CharField(max_length=120, blank=True)
    extra_login_notes = models.TextField(blank=True)
    emergency_contact_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_access_details",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_class_access_details",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Access details for class order {self.class_order.pk}"


class ClassTwoFactorWindow(models.Model):
    """
    Time windows when the client is usually available for 2FA.
    """

    access_detail = models.ForeignKey(
        "class_management.ClassAccessDetail",
        on_delete=models.CASCADE,
        related_name="two_factor_windows",
    )

    weekday = models.PositiveSmallIntegerField(
        help_text="0 is Monday and 6 is Sunday.",
    )
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    timezone = models.CharField(max_length=80, default="Africa/Nairobi")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["weekday", "starts_at"]
        indexes = [
            models.Index(fields=["weekday", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.weekday}: {self.starts_at} to {self.ends_at}"


class ClassTwoFactorRequest(models.Model):
    """
    Operational request for a client to provide or approve 2FA.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="two_factor_requests",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_class_two_factor_codes",
    )

    status = models.CharField(
        max_length=30,
        choices=TwoFactorRequestStatus.choices,
        default=TwoFactorRequestStatus.PENDING,
        db_index=True,
    )

    needed_by = models.DateTimeField(null=True, blank=True)
    request_notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["class_order", "status"]),
        ]

    def mark_resolved(self, *, notes: str = "") -> None:
        self.status = TwoFactorRequestStatus.RESOLVED
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save(
            update_fields=[
                "status",
                "resolution_notes",
                "resolved_at",
            ]
        )


class ClassAccessGrant(models.Model):
    """
    Explicit grant allowing a user to view protected access details.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="access_grants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_access_grants",
    )

    status = models.CharField(
        max_length=30,
        choices=ClassAccessGrantStatus.choices,
        default=ClassAccessGrantStatus.ACTIVE,
        db_index=True,
    )

    reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="granted_class_access_permissions",
    )

    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-granted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_order", "user"],
                condition=models.Q(status=ClassAccessGrantStatus.ACTIVE),
                name="unique_active_class_access_grant",
            )
        ]

    def is_current(self) -> bool:
        if self.status != ClassAccessGrantStatus.ACTIVE:
            return False

        if self.expires_at and self.expires_at <= timezone.now():
            return False

        return True


class ClassAccessLog(models.Model):
    """
    Audit log of credential or sensitive access reads.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="access_logs",
    )
    viewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="class_access_logs",
    )

    reason = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["class_order", "viewed_at"]),
            models.Index(fields=["viewed_by", "viewed_at"]),
        ]