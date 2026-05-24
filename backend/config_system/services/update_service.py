from __future__ import annotations

from dataclasses import asdict
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from config_system.audit.models import ConfigAuditLog
from config_system.cache.keys import build_config_cache_key
from config_system.cache.redis_cache import cache_delete_pattern
from config_system.registry import CONFIG_REGISTRY
from config_system.core.schema import ConfigDefinition, ConfigType
from config_system.storage.models import ConfigItem

User = get_user_model()


class ConfigValidationError(Exception):
    pass


class ConfigUpdateService:
    """
    Centralized runtime config update service.

    Responsibilities:
    1. Validate config existence
    2. Validate type safety
    3. Upsert config
    4. Audit every change
    5. Invalidate caches
    6. Support scoped overrides
    """

    @classmethod
    @transaction.atomic
    def update_config(
        cls,
        *,
        key: str,
        value: Any,
        actor: User | None = None,
        scope: str = "global",
        environment: str = "prod",
        website_id: int | None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
        reason: str = "",
    ) -> ConfigItem:
        definition = cls._get_definition(key)

        cls._validate_environment(
            definition=definition,
            environment=environment,
        )

        cls._validate_type(
            definition=definition,
            value=value,
        )

        config_item, created = ConfigItem.objects.select_for_update().get_or_create(
            key=key,
            scope=scope,
            website_id=website_id,
            tenant_id=tenant_id,
            user_id=user_id,
            defaults={
                "value": value,
                "environment": environment,
                "created_by": actor,
                "updated_by": actor,
                "last_modified_at": timezone.now(),
            },
        )

        previous_value = None if created else config_item.value

        if not created:
            config_item.value = value
            config_item.environment = environment
            config_item.updated_by = actor
            config_item.last_modified_at = timezone.now()
            config_item.save(
                update_fields=[
                    "value",
                    "environment",
                    "updated_by",
                    "last_modified_at",
                    "updated_at",
                ]
            )

        cls._write_audit_log(
            config_item=config_item,
            definition=definition,
            previous_value=previous_value,
            new_value=value,
            actor=actor,
            reason=reason,
        )

        cls._invalidate_cache(
            key=key,
            website_id=website_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        return config_item

    @classmethod
    def bulk_update(
        cls,
        *,
        items: list[dict[str, Any]],
        actor: User | None = None,
    ) -> list[ConfigItem]:
        updated_items: list[ConfigItem] = []

        with transaction.atomic():
            for item in items:
                updated_item = cls.update_config(
                    key=item["key"],
                    value=item["value"],
                    actor=actor,
                    scope=item.get("scope", "global"),
                    environment=item.get("environment", "prod"),
                    website_id=item.get("website_id"),
                    tenant_id=item.get("tenant_id"),
                    user_id=item.get("user_id"),
                    reason=item.get("reason", ""),
                )

                updated_items.append(updated_item)

        return updated_items

    @classmethod
    def deactivate_config(
        cls,
        *,
        key: str,
        actor: User | None = None,
        scope: str = "global",
        website_id: int |None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
        reason: str = "",
    ) -> None:
        config_item = ConfigItem.objects.filter(
            key=key,
            scope=scope,
            website_id=website_id,
            tenant_id=tenant_id,
            user_id=user_id,
            is_active=True,
        ).first()

        if not config_item:
            raise ConfigValidationError(
                f"Config '{key}' does not exist."
            )

        previous_value = config_item.value

        config_item.is_active = False
        config_item.updated_by = actor
        config_item.last_modified_at = timezone.now()

        config_item.save(
            update_fields=[
                "is_active",
                "updated_by",
                "last_modified_at",
                "updated_at",
            ]
        )

        definition = cls._get_definition(key)

        cls._write_audit_log(
            config_item=config_item,
            definition=definition,
            previous_value=previous_value,
            new_value=None,
            actor=actor,
            reason=reason or "Config deactivated",
            action="deactivate",
        )

        cls._invalidate_cache(
            key=key,
            website_id=website_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

    @classmethod
    def rollback_config(
        cls,
        *,
        audit_log_id: int,
        actor: User | None = None,
        reason: str = "",
    ) -> ConfigItem:
        audit_log = ConfigAuditLog.objects.select_related(
            "config_item"
        ).get(id=audit_log_id)

        if audit_log.old_value is None:
            raise ConfigValidationError(
                "Cannot rollback because old_value is empty."
            )

        config_item = audit_log.config_item

        return cls.update_config(
            key=config_item.key,
            value=audit_log.old_value,
            actor=actor,
            scope=config_item.scope,
            environment=config_item.environment,
            website_id=config_item.website_id,
            tenant_id=config_item.tenant_id,
            user_id=config_item.user_id,
            reason=reason or f"Rollback from audit log {audit_log.id}",
        )

    @classmethod
    def _get_definition(
        cls,
        key: str,
    ) -> ConfigDefinition:
        definition = CONFIG_REGISTRY.get(key)

        if not definition:
            raise ConfigValidationError(
                f"Unknown config key '{key}'."
            )

        return definition

    @classmethod
    def _validate_environment(
        cls,
        *,
        definition: ConfigDefinition,
        environment: str,
    ) -> None:
        if environment not in definition.allowed_environments:
            raise ConfigValidationError(
                (
                    f"Config '{definition.key}' "
                    f"is not allowed in '{environment}'."
                )
            )

    @classmethod
    def _validate_type(
        cls,
        *,
        definition: ConfigDefinition,
        value: Any,
    ) -> None:
        config_type = definition.config_type

        validators = {
            ConfigType.BOOL: bool,
            ConfigType.INT: int,
            ConfigType.FLOAT: float,
            ConfigType.STRING: str,
            ConfigType.JSON: (dict, list),
            ConfigType.LIST: list,
        }

        expected_type = validators.get(config_type)

        if expected_type is None:
            raise ConfigValidationError(
                f"Unsupported config type '{config_type}'."
            )

        if not isinstance(value, expected_type):
            raise ConfigValidationError(
                (
                    f"Invalid value type for '{definition.key}'. "
                    f"Expected {config_type.value}, "
                    f"got {type(value).__name__}."
                )
            )

    @classmethod
    def _write_audit_log(
        cls,
        *,
        config_item: ConfigItem,
        definition: ConfigDefinition,
        previous_value: Any,
        new_value: Any,
        actor: User | None,
        reason: str,
        action: str = "update",
    ) -> None:
        ConfigAuditLog.objects.create(
            config_item=config_item,
            key=config_item.key,
            scope=config_item.scope,
            environment=config_item.environment,
            old_value=previous_value,
            new_value=new_value,
            changed_by=actor,
            reason=reason,
            action=action,
            metadata={
                "definition": asdict(definition),
                "website_id": config_item.website_id,
                "tenant_id": config_item.tenant_id,
                "user_id": config_item.user_id,
            },
        )

    @classmethod
    def _invalidate_cache(
        cls,
        *,
        key: str,
        website_id: int | None,
        tenant_id: int | None,
        user_id: int | None,
    ) -> None:
        exact_key = build_config_cache_key(
            key=key,
            website_id=website_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        cache_delete_pattern(exact_key)

        wildcard_pattern = f"config:{key}:*"

        cache_delete_pattern(wildcard_pattern)
