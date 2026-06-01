from __future__ import annotations

from typing import Any

from django.core.cache import cache

from config_system.cache.keys import build_config_cache_key
from config_system.registry import CONFIG_REGISTRY
from config_system.core.schema import ConfigType
from config_system.storage.models import ConfigItem
from config_system.rollout.cohort_engine import CohortEngine as RolloutEngine


class ConfigEvaluationError(Exception):
    pass


class ConfigEvaluator:
    """
    Single source of truth for config resolution.

    Order:
        1. kill switch (hard override)
        2. rollout engine (feature exposure)
        3. user
        4. tenant
        5. website
        6. global
        7. registry default
    """

    @classmethod
    def get(
        cls,
        key: str,
        *,
        user_id: int | None = None,
        tenant_id: int | None = None,
        website_id: int | None = None,
        use_cache: bool = True,
        rollout_percentage: float | None = None,
    ) -> Any:

        # -------------------------
        # 1. Kill Switch (HARD STOP)
        # -------------------------
        from config_system.rollout.kill_switch import KillSwitchEngine # local to break circular import
        if KillSwitchEngine.is_disabled(
            key=key,
            user_id=user_id,
            tenant_id=tenant_id,
            website_id=website_id,
        ):
            return False

        # -------------------------
        # 2. Rollout Gate (optional feature exposure)
        # -------------------------
        if rollout_percentage is not None:
            if not RolloutEngine.is_enabled(
                key=key,
                percentage=rollout_percentage,
                user_id=user_id,
                tenant_id=tenant_id,
                website_id=website_id,
            ):
                return False

        cache_key = build_config_cache_key(
            key=key,
            user_id=user_id,
            tenant_id=tenant_id,
            website_id=website_id,
        )

        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        definition = CONFIG_REGISTRY.get(key)
        if not definition:
            raise ConfigEvaluationError(f"Config key not registered: {key}")

        value = (
            cls._get_user_level(key, user_id)
            or cls._get_tenant_level(key, tenant_id)
            or cls._get_website_level(key, website_id)
            or cls._get_global_level(key)
            or definition.default
        )

        value = cls._coerce_type(value, definition.config_type)

        if use_cache:
            cache.set(cache_key, value, definition.cache_ttl_seconds)

        return value

    # -----------------------------
    # Resolution Layers
    # -----------------------------

    @classmethod
    def _get_user_level(cls, key: str, user_id: int | None) -> Any:
        if not user_id:
            return None

        obj = ConfigItem.objects.filter(
            key=key,
            user_id=user_id,
            is_active=True,
        ).first()

        return obj.value if obj else None

    @classmethod
    def _get_tenant_level(cls, key: str, tenant_id: int | None) -> Any:
        if not tenant_id:
            return None

        obj = ConfigItem.objects.filter(
            key=key,
            tenant_id=tenant_id,
            is_active=True,
        ).first()

        return obj.value if obj else None

    @classmethod
    def _get_website_level(cls, key: str, website_id: int | None) -> Any:
        if not website_id:
            return None

        obj = ConfigItem.objects.filter(
            key=key,
            website_id=website_id,
            is_active=True,
        ).first()

        return obj.value if obj else None

    @classmethod
    def _get_global_level(cls, key: str) -> Any:
        obj = ConfigItem.objects.filter(
            key=key,
            scope="global",
            is_active=True,
        ).first()

        return obj.value if obj else None

    # -----------------------------
    # Type Safety
    # -----------------------------

    @classmethod
    def _coerce_type(cls, value: Any, config_type: ConfigType) -> Any:
        if value is None:
            return None

        if config_type == ConfigType.BOOL:
            return bool(value)

        if config_type == ConfigType.INT:
            return int(value)

        if config_type == ConfigType.FLOAT:
            return float(value)

        if config_type == ConfigType.STRING:
            return str(value)

        if config_type in (ConfigType.JSON, ConfigType.LIST):
            return value

        return value
