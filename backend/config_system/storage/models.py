from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


# ============================================================
# Shared Mixins
# ============================================================

class TimestampMixin(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class ActorTrackingMixin(models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_configs",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_configs",
    )

    class Meta:
        abstract = True


# ============================================================
# Config Item
# ============================================================

class ConfigScope(models.TextChoices):

    GLOBAL = "global", "Global"
    TENANT = "tenant", "Tenant"
    WEBSITE = "website", "Website"
    USER = "user", "User"


class ConfigItem(
    TimestampMixin,
    ActorTrackingMixin,
):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    key = models.CharField(
        max_length=255,
        db_index=True,
    )

    value = models.JSONField()

    scope = models.CharField(
        max_length=20,
        choices=ConfigScope.choices,
        default=ConfigScope.GLOBAL,
        db_index=True,
    )

    environment = models.CharField(
        max_length=32,
        default="prod",
        db_index=True,
    )

    # --------------------------------------------------------
    # Scope Resolution Targets
    # --------------------------------------------------------

    website_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    tenant_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    user_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    # --------------------------------------------------------
    # Operational Metadata
    # --------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    last_modified_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
        default="",
    )

    class Meta:

        db_table = "config_items"

        ordering = (
            "key",
            "-updated_at",
        )

        indexes = [

            # Core runtime lookup
            models.Index(
                fields=[
                    "key",
                    "scope",
                    "is_active",
                ],
                name="config_core_lookup_idx",
            ),

            # Tenant resolution
            models.Index(
                fields=[
                    "key",
                    "tenant_id",
                    "is_active",
                ],
                name="config_tenant_lookup_idx",
            ),

            # Website resolution
            models.Index(
                fields=[
                    "key",
                    "website_id",
                    "is_active",
                ],
                name="config_website_lookup_idx",
            ),

            # User resolution
            models.Index(
                fields=[
                    "key",
                    "user_id",
                    "is_active",
                ],
                name="config_user_lookup_idx",
            ),

            # Environment targeting
            models.Index(
                fields=[
                    "environment",
                    "is_active",
                ],
                name="config_env_lookup_idx",
            ),
        ]

        constraints = [

            # Prevent duplicate global keys
            models.UniqueConstraint(
                fields=[
                    "key",
                    "scope",
                    "environment",
                    "website_id",
                    "tenant_id",
                    "user_id",
                ],
                condition=models.Q(
                    is_active=True,
                ),
                name="unique_active_config_scope",
            ),
        ]

    def __str__(self) -> str:

        return (
            f"{self.key} "
            f"[{self.scope}]"
        )


# ============================================================
# Audit Models
# ============================================================

class ConfigAuditAction(models.TextChoices):

    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"


class ConfigAuditLog(TimestampMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    config_item = models.ForeignKey(
        ConfigItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )

    key = models.CharField(
        max_length=255,
        db_index=True,
    )

    scope = models.CharField(
        max_length=20,
        db_index=True,
    )

    environment = models.CharField(
        max_length=32,
        db_index=True,
    )

    action = models.CharField(
        max_length=20,
        choices=ConfigAuditAction.choices,
        db_index=True,
    )

    old_value = models.JSONField(
        null=True,
        blank=True,
    )

    new_value = models.JSONField(
        null=True,
        blank=True,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="config_changes",
    )

    reason = models.TextField(
        blank=True,
        default="",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:

        db_table = "config_audit_logs"

        ordering = (
            "-created_at",
        )

        indexes = [

            models.Index(
                fields=[
                    "key",
                    "created_at",
                ],
                name="config_audit_key_idx",
            ),

            models.Index(
                fields=[
                    "action",
                    "created_at",
                ],
                name="config_audit_action_idx",
            ),
        ]

    def __str__(self) -> str:

        return (
            f"{self.key} "
            f"[{self.action}]"
        )