from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from config_system.storage.models import ConfigItem


class ConfigSelectors:
    """
    Pure data access layer for ConfigItem.

    Rules:
        - NO business logic
        - NO caching logic
        - NO rollout logic
        - NO kill switch logic
        - ONLY optimized queries
    """

    # ---------------------------------------------------------
    # Base Query
    # ---------------------------------------------------------

    @staticmethod
    def base_queryset() -> QuerySet[ConfigItem]:
        return ConfigItem.objects.filter(is_active=True)

    # ---------------------------------------------------------
    # Key Lookup
    # ---------------------------------------------------------

    @staticmethod
    def by_key(
        key: str,
    ) -> QuerySet[ConfigItem]:

        return ConfigSelectors.base_queryset().filter(
            key=key,
        )

    # ---------------------------------------------------------
    # Scope Filters
    # ---------------------------------------------------------

    @staticmethod
    def for_user(
        key: str,
        user_id: int,
    ) -> QuerySet[ConfigItem]:

        return ConfigSelectors.by_key(key).filter(
            user_id=user_id,
        )

    @staticmethod
    def for_tenant(
        key: str,
        tenant_id: int,
    ) -> QuerySet[ConfigItem]:

        return ConfigSelectors.by_key(key).filter(
            tenant_id=tenant_id,
        )

    @staticmethod
    def for_website(
        key: str,
        website_id: int,
    ) -> QuerySet[ConfigItem]:

        return ConfigSelectors.by_key(key).filter(
            website_id=website_id,
        )

    @staticmethod
    def global_only(
        key: str,
    ) -> QuerySet[ConfigItem]:

        return ConfigSelectors.by_key(key).filter(
            scope="global",
        )

    # ---------------------------------------------------------
    # Resolution Helpers
    # ---------------------------------------------------------

    @staticmethod
    def resolve_best_match(
        *,
        key: str,
        user_id: int | None = None,
        tenant_id: int | None = None,
        website_id: int | None = None,
    ) -> ConfigItem | None:

        """
        Strict resolution priority:
            1. user
            2. tenant
            3. website
            4. global
        """

        if user_id:
            obj = ConfigSelectors.for_user(
                key,
                user_id,
            ).first()

            if obj:
                return obj

        if tenant_id:
            obj = ConfigSelectors.for_tenant(
                key,
                tenant_id,
            ).first()

            if obj:
                return obj

        if website_id:
            obj = ConfigSelectors.for_website(
                key,
                website_id,
            ).first()

            if obj:
                return obj

        return ConfigSelectors.global_only(
            key,
        ).first()

    # ---------------------------------------------------------
    # Bulk Operations
    # ---------------------------------------------------------

    @staticmethod
    def list_keys() -> list[str]:

        return list(
            ConfigItem.objects
            .filter(is_active=True)
            .values_list("key", flat=True)
            .distinct()
        )

    @staticmethod
    def exists(
        key: str,
    ) -> bool:

        return ConfigSelectors.by_key(
            key
        ).exists()

    # ---------------------------------------------------------
    # Scoped Queries
    # ---------------------------------------------------------

    @staticmethod
    def scoped(
        *,
        scope: str,
        scope_id: int,
        key: str,
    ) -> QuerySet[ConfigItem]:

        if scope == "user":
            return ConfigSelectors.for_user(key, scope_id)

        if scope == "tenant":
            return ConfigSelectors.for_tenant(key, scope_id)

        if scope == "website":
            return ConfigSelectors.for_website(key, scope_id)

        return ConfigSelectors.global_only(key)