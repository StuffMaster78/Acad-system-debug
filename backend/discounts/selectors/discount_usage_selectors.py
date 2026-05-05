from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet
from django.db.models import Sum

from discounts.models import DiscountUsage


class DiscountUsageSelector:
    """
    Read queries for discount usage records.
    """

    @staticmethod
    def base_queryset(*, website) -> QuerySet[DiscountUsage]:
        """
        Return tenant-scoped discount usage records.
        """
        return (
            DiscountUsage.objects.filter(website=website)
            .select_related("website", "discount", "client")
        )

    @classmethod
    def get_for_payable(
        cls,
        *,
        website,
        payable_type: str,
        payable_id: str,
    ) -> DiscountUsage | None:
        """
        Return discount usage for a payable object.
        """
        return (
            cls.base_queryset(website=website)
            .filter(
                payable_type=payable_type,
                payable_id=str(payable_id),
            )
            .first()
        )

    @classmethod
    def exists_for_payable(
        cls,
        *,
        website,
        payable_type: str,
        payable_id: str,
    ) -> bool:
        """
        Return whether a payable object already used a discount.
        """
        return (
            cls.base_queryset(website=website)
            .filter(
                payable_type=payable_type,
                payable_id=str(payable_id),
            )
            .exists()
        )

    @classmethod
    def count_for_discount(cls, *, website, discount) -> int:
        """
        Return tenant-scoped usage count for a discount.
        """
        return cls.base_queryset(website=website).filter(
            discount=discount,
        ).count()

    @classmethod
    def count_for_client_discount(
        cls,
        *,
        website,
        discount,
        client,
    ) -> int:
        """
        Return tenant-scoped usage count for a client and discount.
        """
        return cls.base_queryset(website=website).filter(
            discount=discount,
            client=client,
        ).count()

    @classmethod
    def list_for_client(
        cls,
        *,
        website,
        client,
    ) -> QuerySet[DiscountUsage]:
        """
        Return all tenant-scoped discount usages for a client.
        """
        return cls.base_queryset(website=website).filter(client=client)

    @classmethod
    def list_for_discount(
        cls,
        *,
        website,
        discount,
    ) -> QuerySet[DiscountUsage]:
        """
        Return all tenant-scoped usage records for a discount.
        """
        return cls.base_queryset(website=website).filter(
            discount=discount,
        )

    @classmethod
    def get_total_discount_given(cls, *, website) -> Decimal:
        """
        Return total discount amount given for a website.
        """
        result = cls.base_queryset(website=website).aggregate(
            total=Sum("discount_amount"),
        )

        return result["total"] or Decimal("0.00")

    @classmethod
    def get_client_usage_remaining(
        cls,
        *,
        website,
        discount,
        client,
    ) -> int | None:
        """
        Return how many times a client can still use this discount.
        """
        if discount.per_client_usage_limit is None:
            return None

        used = cls.count_for_client_discount(
            website=website,
            discount=discount,
            client=client,
        )

        return max(discount.per_client_usage_limit - used, 0)