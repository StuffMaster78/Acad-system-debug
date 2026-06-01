from __future__ import annotations

from decimal import Decimal

from django.db.models import Count
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from discounts.models import PromotionalCampaign


class CampaignSelector:
    """
    Read queries for promotional campaigns.
    """

    @staticmethod
    def base_queryset(
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return tenant-scoped campaigns.
        """
        return (
            PromotionalCampaign.objects.filter(
                website=website,
            )
            .select_related("website", "created_by", "updated_by")
            .prefetch_related("discounts")
        )

    @classmethod
    def list_active(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return active, non-archived campaigns.
        """
        return cls.base_queryset(website=website).filter(
            is_active=True,
            is_archived=False,
        )

    @classmethod
    def list_running(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return campaigns currently within their time window.
        """
        now = timezone.now()

        return cls.list_active(website=website).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        )

    @classmethod
    def list_scheduled(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return campaigns scheduled for the future.
        """
        return cls.base_queryset(website=website).filter(
            is_active=True,
            is_archived=False,
            starts_at__gt=timezone.now(),
        )

    @classmethod
    def list_expired(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return campaigns whose end date has passed.
        """
        return cls.base_queryset(website=website).filter(
            ends_at__lt=timezone.now(),
        )

    @classmethod
    def list_with_metrics(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return campaigns with usage metrics.
        """
        return cls.base_queryset(website=website).annotate(
            discount_count=Count("discounts", distinct=True),
            usage_count=Count(
                "discounts__usages",
                distinct=True,
            ),
            distinct_clients=Count(
                "discounts__usages__client",
                distinct=True,
            ),
            total_discount_given=Coalesce(
                Sum("discounts__usages__discount_amount"),
                Decimal("0.00"),
            ),
        )


    @classmethod
    def list_public_calendar_campaigns(
        cls,
        *,
        website,
    ) -> QuerySet[PromotionalCampaign]:
        """
        Return campaigns visible on the client calendar.
        """
        return (
            cls.base_queryset(website=website)
            .filter(is_archived=False)
            .filter(
                Q(is_active=True)
                | Q(starts_at__gte=timezone.now())
            )
            .prefetch_related("discounts")
            .order_by("starts_at", "name")
        )