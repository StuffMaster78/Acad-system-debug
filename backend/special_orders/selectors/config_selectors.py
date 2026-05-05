from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrderMilestoneTemplate,
    SpecialOrderWriterPayRule,
)


class SpecialOrderConfigSelector:
    """
    Tenant-safe read layer for special order configs.
    """

    @staticmethod
    def list_predefined_configs(
        *,
        website,
        active_only: bool = True,
    ) -> QuerySet[PredefinedSpecialOrderConfig]:
        queryset = (
            PredefinedSpecialOrderConfig.objects.filter(
                website=website,
            )
            .prefetch_related("durations")
            .order_by("name")
        )

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset

    @staticmethod
    def get_predefined_config(
        *,
        website,
        config_id: int,
    ) -> PredefinedSpecialOrderConfig:
        return (
            PredefinedSpecialOrderConfig.objects.prefetch_related(
                "durations",
            )
            .get(
                id=config_id,
                website=website,
            )
        )

    @staticmethod
    def get_duration(
        *,
        website,
        duration_id: int,
    ) -> PredefinedSpecialOrderDuration:
        return (
            PredefinedSpecialOrderDuration.objects.select_related(
                "predefined_order",
            )
            .get(
                id=duration_id,
                website=website,
            )
        )

    @staticmethod
    def get_estimated_settings(
        *,
        website,
    ) -> EstimatedSpecialOrderSettings:
        settings, _created = (
            EstimatedSpecialOrderSettings.objects.get_or_create(
                website=website,
            )
        )
        return settings

    @staticmethod
    def list_milestone_templates(
        *,
        website,
        active_only: bool = True,
    ) -> QuerySet[SpecialOrderMilestoneTemplate]:
        queryset = (
            SpecialOrderMilestoneTemplate.objects.filter(
                website=website,
            )
            .prefetch_related("items")
            .order_by("name")
        )

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset

    @staticmethod
    def list_writer_pay_rules(
        *,
        website,
        active_only: bool = True,
    ) -> QuerySet[SpecialOrderWriterPayRule]:
        queryset = SpecialOrderWriterPayRule.objects.filter(
            website=website,
        ).order_by("name")

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset