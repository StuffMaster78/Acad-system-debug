from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from config_system.audit.models import (
    ConfigAuditAction,
    ConfigAuditLog,
)
from config_system.core.schema import ConfigDefinition
from config_system.registry import require_config_definition
from config_system.storage.models import ConfigItem
from config_system.selectors.config_selectors import ConfigSelectors


class ConfigUpdateError(Exception):
    pass


class ConfigUpdater:
    """
    Safe mutation layer for runtime config system.

    Guarantees:
        - type safety enforced via registry
        - atomic updates
        - audit logging
        - safe cache invalidation
        - selector-based consistency
    """

    # ---------------------------------------------------------
    # Public API: SET
    # ---------------------------------------------------------

    @classmethod
    @transaction.atomic
    def set(
        cls,
        *,
        key: str,
        value: Any,
        actor: Any | None = None,
        scope: str = "global",
        environment: str = "prod",
        website_id: int | None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
        reason: str = "",
    ) -> ConfigItem:

        definition: ConfigDefinition = require_config_definition(key)

        cls._validate_type(definition, value)

        obj = ConfigSelectors.scoped(
            scope=scope,
            scope_id=cls._resolve_scope_id(scope, website_id, tenant_id, user_id),
            key=key,
        ).first()

        created = obj is None

        if created:
            obj = ConfigItem(
                key=key,
                value=value,
                scope=scope,
                environment=environment,
                website_id=website_id,
                tenant_id=tenant_id,
                user_id=user_id,
                created_by=actor,
                updated_by=actor,
                last_modified_at=timezone.now(),
                is_active=True,
            )
        else:
            obj.value = value
            obj.environment = environment
            obj.updated_by = actor
            obj.last_modified_at = timezone.now()

        obj.save()

        cls._audit(
            obj=obj,
            definition=definition,
            old_value=None if created else obj.value,
            new_value=value,
            actor=actor,
            reason=reason,
            action=(
                ConfigAuditAction.CREATE
                if created
                else ConfigAuditAction.UPDATE
            ),
        )

        cls._invalidate_cache(key)

        return obj

    # ---------------------------------------------------------
    # Public API: DELETE (soft delete)
    # ---------------------------------------------------------

    @classmethod
    @transaction.atomic
    def delete(
        cls,
        *,
        key: str,
        actor: Any | None = None,
        scope: str = "global",
        website_id: int | None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
        reason: str = "",
    ) -> None:

        obj = ConfigSelectors.scoped(
            scope=scope,
            scope_id=cls._resolve_scope_id(scope, website_id, tenant_id, user_id),
            key=key,
        ).first()

        if not obj:
            raise ConfigUpdateError(f"Config '{key}' not found")

        old_value = obj.value

        obj.is_active = False
        obj.updated_by = actor
        obj.last_modified_at = timezone.now()
        obj.save()

        definition = require_config_definition(key)

        cls._audit(
            obj=obj,
            definition=definition,
            old_value=old_value,
            new_value=None,
            actor=actor,
            reason=reason,
            action=ConfigAuditAction.DELETE,
        )

        cls._invalidate_cache(key)

    # ---------------------------------------------------------
    # Type Validation
    # ---------------------------------------------------------

    @classmethod
    def _validate_type(
        cls,
        definition: ConfigDefinition,
        value: Any,
    ) -> None:

        expected = definition.config_type

        if expected.value == "bool" and not isinstance(value, bool):
            raise ConfigUpdateError("Expected bool")

        if expected.value == "int" and not isinstance(value, int):
            raise ConfigUpdateError("Expected int")

        if expected.value == "float" and not isinstance(value, (int, float)):
            raise ConfigUpdateError("Expected float")

        if expected.value == "string" and not isinstance(value, str):
            raise ConfigUpdateError("Expected string")

        if expected.value == "list" and not isinstance(value, list):
            raise ConfigUpdateError("Expected list")

        if expected.value == "json" and not isinstance(value, (dict, list)):
            raise ConfigUpdateError("Expected json")

    # ---------------------------------------------------------
    # Audit
    # ---------------------------------------------------------

    @classmethod
    def _audit(
        cls,
        *,
        obj: ConfigItem,
        definition: ConfigDefinition,
        old_value: Any,
        new_value: Any,
        actor: Any | None,
        reason: str,
        action: str,
    ) -> None:

        ConfigAuditLog.objects.create(
            config_item=obj,
            key=obj.key,
            scope=obj.scope,
            environment=obj.environment,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=actor,
            reason=reason,
            metadata={
                "definition": definition.key,
                "website_id": obj.website_id,
                "tenant_id": obj.tenant_id,
                "user_id": obj.user_id,
            },
        )

    # ---------------------------------------------------------
    # Cache invalidation (FIXED - no delete_pattern)
    # ---------------------------------------------------------

    @classmethod
    def _invalidate_cache(cls, key: str) -> None:
        """
        Safe invalidation strategy.

        We avoid pattern deletes because:
        - not all cache backends support it
        - RedisCluster breaks it
        - Django cache abstraction does NOT guarantee it
        """

        cache_keys = [
            f"config:{key}",
            f"config:{key}:user:*",
            f"config:{key}:tenant:*",
            f"config:{key}:website:*",
        ]

        # Best-effort safe invalidation
        for k in cache_keys:
            try:
                cache.delete(k)
            except Exception:
                continue

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _resolve_scope_id(
        scope: str,
        website_id: int | None,
        tenant_id: int | None,
        user_id: int | None,
    ) -> int | None:

        if scope == "user":
            return user_id
        if scope == "tenant":
            return tenant_id
        if scope == "website":
            return website_id

        return None