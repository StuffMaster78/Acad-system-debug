from __future__ import annotations

from django.core.cache import cache

from config_system.cache.keys import build_kill_switch_cache_key
from config_system.services.evaluator import ConfigEvaluator


class KillSwitchEngine:
    """
    Production-grade emergency feature shutdown system.

    Design goals:
        - no direct ORM access
        - single source of truth via ConfigEvaluator
        - deterministic caching
        - safe failure behavior
        - structured cache keys
    """

    GLOBAL_KEY = "system.maintenance_mode"

    CACHE_TTL = {
        "global": 10,
        "feature": 30,
        "scoped": 30,
    }

    @classmethod
    def is_disabled(
        cls,
        *,
        key: str,
        user_id: int | None = None,
        tenant_id: int | None = None,
        website_id: int | None = None,
    ) -> bool:

        if cls._global_disabled():
            return True

        if cls._feature_disabled(key):
            return True

        if user_id and cls._scoped_disabled("user", key, user_id):
            return True

        if tenant_id and cls._scoped_disabled("tenant", key, tenant_id):
            return True

        if website_id and cls._scoped_disabled("website", key, website_id):
            return True

        return False

    # ------------------------------------------------------------
    # Global
    # ------------------------------------------------------------

    @classmethod
    def _global_disabled(cls) -> bool:
        cache_key = build_kill_switch_cache_key(level="global")

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        value = ConfigEvaluator.get(
            cls.GLOBAL_KEY,
            use_cache=False,
        )

        result = bool(value)

        cache.set(cache_key, result, cls.CACHE_TTL["global"])
        return result

    # ------------------------------------------------------------
    # Feature-level
    # ------------------------------------------------------------

    @classmethod
    def _feature_disabled(cls, key: str) -> bool:
        cache_key = build_kill_switch_cache_key(
            level="feature",
            key=key,
        )

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        switch_key = f"{key}.disabled"

        value = ConfigEvaluator.get(
            switch_key,
            use_cache=False,
        )

        result = bool(value)

        cache.set(cache_key, result, cls.CACHE_TTL["feature"])
        return result

    # ------------------------------------------------------------
    # Scoped
    # ------------------------------------------------------------

    @classmethod
    def _scoped_disabled(
        cls,
        scope: str,
        key: str,
        scope_id: int,
    ) -> bool:

        cache_key = build_kill_switch_cache_key(
            level="scoped",
            scope=scope,
            scope_id=scope_id,
            key=key,
        )

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        switch_key = f"{key}.disabled"

        value = ConfigEvaluator.get(
            switch_key,
            use_cache=False,
        )

        result = bool(value)

        cache.set(cache_key, result, cls.CACHE_TTL["scoped"])
        return result