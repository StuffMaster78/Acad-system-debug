from __future__ import annotations

from django.db.models import Count, Sum
from django.db.models import Q
from django.db.models import QuerySet
from django.utils import timezone
from django.db.models.functions import Coalesce
from decimal import Decimal

from discounts.constants import DiscountOrigin
from discounts.models.discount import Discount


class DiscountSelector:
    """
    Read queries for discount records.
    """

    @staticmethod
    def base_queryset(*, website) -> QuerySet[Discount]:
        """
        Return tenant-scoped, non-deleted discounts.
        """
        return (
            Discount.objects.filter(
                website=website,
                is_deleted=False,
            )
            .select_related("website", "campaign", "created_by")
            .prefetch_related("eligible_clients")
        )

    @classmethod
    def get_by_id(cls, *, website, discount_id: int) -> Discount | None:
        """
        Return a discount by ID for a website.
        """
        return cls.base_queryset(website=website).filter(
            id=discount_id,
        ).first()

    @classmethod
    def get_by_code(cls, *, website, code: str) -> Discount | None:
        """
        Return a discount by code for a website.
        """
        normalized_code = code.strip().upper()

        return cls.base_queryset(website=website).filter(
            discount_code=normalized_code,
        ).first()

    @classmethod
    def list_active(cls, *, website) -> QuerySet[Discount]:
        """
        Return active, non-archived discounts.
        """
        return cls.base_queryset(website=website).filter(
            is_active=True,
            is_archived=False,
        )

    @classmethod
    def list_working(cls, *, website) -> QuerySet[Discount]:
        """
        Return discounts currently usable by time and campaign state.
        """
        now = timezone.now()

        return cls.list_active(website=website).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
            Q(campaign__isnull=True)
            | (
                Q(campaign__is_active=True)
                & Q(campaign__is_archived=False)
            ),
        )

    @classmethod
    def list_scheduled(cls, *, website) -> QuerySet[Discount]:
        """
        Return discounts scheduled for future activation.
        """
        return cls.base_queryset(website=website).filter(
            is_active=True,
            is_archived=False,
            starts_at__gt=timezone.now(),
        )

    @classmethod
    def list_expired(cls, *, website) -> QuerySet[Discount]:
        """
        Return discounts whose end date has passed.
        """
        return cls.base_queryset(website=website).filter(
            ends_at__lt=timezone.now(),
        )

    @classmethod
    def list_archived(cls, *, website) -> QuerySet[Discount]:
        """
        Return archived discounts.
        """
        return cls.base_queryset(website=website).filter(
            is_archived=True,
        )

    @classmethod
    def list_by_origin(
        cls,
        *,
        website,
        origin: str,
    ) -> QuerySet[Discount]:
        """
        Return discounts by origin.
        """
        return cls.base_queryset(website=website).filter(origin=origin)

    @classmethod
    def list_holiday_discounts(cls, *, website) -> QuerySet[Discount]:
        """
        Return holiday generated discounts.
        """
        return cls.list_by_origin(
            website=website,
            origin=DiscountOrigin.HOLIDAY,
        )

    @classmethod
    def list_loyalty_discounts(cls, *, website) -> QuerySet[Discount]:
        """
        Return loyalty generated discounts.
        """
        return cls.list_by_origin(
            website=website,
            origin=DiscountOrigin.LOYALTY,
        )

    @classmethod
    def list_with_usage_counts(
        cls,
        *,
        website
    ) -> QuerySet[Discount]:
        """
        Return discounts annotated with usage metrics.

        Includes:
            - usage_count
            - total_discount_given
            - distinct_clients
        """
        return cls.base_queryset(website=website).annotate(
            usage_count=Count("usages", distinct=True),
            total_discount_given=Coalesce(
                Sum("usages__discount_amount"),
                Decimal("0.00"),
            ),
            distinct_clients=Count(
                "usages__client",
                distinct=True,
            ),
        )