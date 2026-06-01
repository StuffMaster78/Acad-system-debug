from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    InstitutionType,
    SensitiveAccessAction,
    SensitiveAccessLevel,
    SpecialOrderPlatform,
    TwoFactorMethod,
    TwoFactorRequestStatus,
)


class SpecialOrderInstitutionProfile(TimeStampedModel):
    """
    Institution and course context for a special order.

    This supports operations, coordination, pricing intelligence,
    and marketing analytics.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_institution_profiles",
    )
    special_order = models.OneToOneField(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="institution_profile",
    )

    institution_name = models.CharField(max_length=255)
    institution_type = models.CharField(
        max_length=50,
        choices=InstitutionType.CHOICES,
        default=InstitutionType.UNIVERSITY,
    )

    country = models.CharField(max_length=100, blank=True)
    state_region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    program_name = models.CharField(max_length=255, blank=True)
    course_code = models.CharField(max_length=100, blank=True)
    course_name = models.CharField(max_length=255, blank=True)
    instructor_name = models.CharField(max_length=255, blank=True)
    term_or_semester = models.CharField(max_length=100, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("institution_name",)
        indexes = [
            models.Index(fields=["website", "institution_name"]),
            models.Index(fields=["website", "institution_type"]),
            models.Index(fields=["website", "program_name"]),
            models.Index(fields=["website", "course_code"]),
        ]

    def __str__(self) -> str:
        return self.institution_name

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderPlatformAccessVault(TimeStampedModel):
    """
    Protected platform/login vault for special orders.

    Passwords should be encrypted before storage. Do not expose this model
    directly through normal order serializers.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_access_vaults",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="access_vaults",
    )

    platform = models.CharField(
        max_length=80,
        choices=SpecialOrderPlatform.CHOICES,
        default=SpecialOrderPlatform.OTHER,
    )
    platform_label = models.CharField(max_length=255, blank=True)

    login_url = models.URLField(max_length=1000, blank=True)
    username = models.CharField(max_length=255, blank=True)
    encrypted_password = models.TextField(blank=True)

    recovery_email = models.EmailField(blank=True)
    recovery_phone_last4 = models.CharField(max_length=10, blank=True)

    access_notes = models.TextField(blank=True)
    requires_2fa = models.BooleanField(default=False)
    preferred_2fa_method = models.CharField(
        max_length=50,
        choices=TwoFactorMethod.CHOICES,
        blank=True,
    )
    preferred_2fa_window_start = models.TimeField(null=True, blank=True)
    preferred_2fa_window_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=100, default="UTC")

    is_active = models.BooleanField(default=True)
    last_rotated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_access_vaults",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "platform"]),
            models.Index(fields=["website", "is_active"]),
        ]

    def __str__(self) -> str:
        return (
            f"AccessVault(order={self.special_order_id}, "
            f"platform={self.platform})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderExternalLink(TimeStampedModel):
    """
    External link related to a special order.

    Use this for assignment pages, shared docs, rubrics, portals,
    LMS pages, and non-password resources.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_external_links",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="external_links",
    )

    label = models.CharField(max_length=255)
    url = models.URLField(max_length=1000)
    link_type = models.CharField(max_length=80, default="other")
    requires_login = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_external_links",
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("label",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "link_type"]),
        ]

    def __str__(self) -> str:
        return self.label

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderAccessGrant(TimeStampedModel):
    """
    Explicit grant allowing non-admin users to access sensitive details.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_access_grants",
    )
    vault = models.ForeignKey(
        "special_orders.SpecialOrderPlatformAccessVault",
        on_delete=models.CASCADE,
        related_name="access_grants",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="sensitive_access_grants",
    )

    granted_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_order_sensitive_access_grants",
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_special_order_sensitive_access",
    )

    access_level = models.CharField(
        max_length=50,
        choices=SensitiveAccessLevel.CHOICES,
    )
    reason = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revoked_special_order_sensitive_access",
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "vault"]),
            models.Index(fields=["website", "granted_to"]),
            models.Index(fields=["website", "expires_at"]),
            models.Index(fields=["website", "revoked_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"AccessGrant(vault={self.vault_id}, "
            f"user={self.granted_to_id})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        vault_id: int
        special_order_id: int
        granted_to_id: int


class SpecialOrderAccessLog(TimeStampedModel):
    """
    Immutable audit log for sensitive access actions.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_access_logs",
    )
    vault = models.ForeignKey(
        "special_orders.SpecialOrderPlatformAccessVault",
        on_delete=models.CASCADE,
        related_name="access_logs",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="sensitive_access_logs",
    )

    accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="special_order_sensitive_access_logs",
    )
    action = models.CharField(
        max_length=80,
        choices=SensitiveAccessAction.CHOICES,
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "vault"]),
            models.Index(fields=["website", "accessed_by"]),
            models.Index(fields=["website", "action"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"AccessLog(vault={self.vault_id}, "
            f"action={self.action})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        vault_id: int
        special_order_id: int


class SpecialOrderTwoFactorRequest(TimeStampedModel):
    """
    Coordinates 2FA requests with clients.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_two_factor_requests",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="two_factor_requests",
    )
    vault = models.ForeignKey(
        "special_orders.SpecialOrderPlatformAccessVault",
        on_delete=models.CASCADE,
        related_name="two_factor_requests",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_special_order_two_factor_codes",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_order_two_factor_requests",
    )

    status = models.CharField(
        max_length=50,
        choices=TwoFactorRequestStatus.CHOICES,
        default=TwoFactorRequestStatus.PENDING,
    )

    preferred_method = models.CharField(
        max_length=50,
        choices=TwoFactorMethod.CHOICES,
        blank=True,
    )
    message = models.TextField(blank=True)

    requested_for_time = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    code_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional reference if code is stored elsewhere.",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "vault"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "expires_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"TwoFactorRequest(order={self.special_order_id}, "
            f"status={self.status})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        vault_id: int
        client_id: int