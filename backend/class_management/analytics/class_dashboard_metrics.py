from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Q, Sum

from class_management.constants import (
    ClassOrderStatus,
    ClassPaymentStatus,
)
from class_management.models import ClassOrder


class ClassDashboardMetrics:
    """
    High-level class management dashboard metrics.
    """

    @staticmethod
    def get_summary(*, website) -> dict:
        """
        Return top-level operational and financial metrics.
        """
        queryset = ClassOrder.objects.filter(website=website)

        totals = queryset.aggregate(
            total_classes=Count("id"),
            active_classes=Count(
                "id",
                filter=Q(
                    status__in=[
                        ClassOrderStatus.SUBMITTED,
                        ClassOrderStatus.UNDER_REVIEW,
                        ClassOrderStatus.PRICE_PROPOSED,
                        ClassOrderStatus.NEGOTIATING,
                        ClassOrderStatus.ACCEPTED,
                        ClassOrderStatus.PENDING_PAYMENT,
                        ClassOrderStatus.PARTIALLY_PAID,
                        ClassOrderStatus.PAID,
                        ClassOrderStatus.ASSIGNED,
                        ClassOrderStatus.IN_PROGRESS,
                    ]
                ),
            ),
            completed_classes=Count(
                "id",
                filter=Q(status=ClassOrderStatus.COMPLETED),
            ),
            cancelled_classes=Count(
                "id",
                filter=Q(status=ClassOrderStatus.CANCELLED),
            ),
            unpaid_classes=Count(
                "id",
                filter=Q(payment_status=ClassPaymentStatus.UNPAID),
            ),
            partially_paid_classes=Count(
                "id",
                filter=Q(payment_status=ClassPaymentStatus.PARTIALLY_PAID),
            ),
            paid_classes=Count(
                "id",
                filter=Q(payment_status=ClassPaymentStatus.PAID),
            ),
            quoted_total=Sum("quoted_amount"),
            discount_total=Sum("discount_amount"),
            final_total=Sum("final_amount"),
            paid_total=Sum("paid_amount"),
            balance_total=Sum("balance_amount"),
        )

        return {
            key: value if value is not None else Decimal("0.00")
            for key, value in totals.items()
        }