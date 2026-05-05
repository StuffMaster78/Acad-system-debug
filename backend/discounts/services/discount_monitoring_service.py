from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models import F
from django.utils import timezone

from discounts.models.discount import Discount
from discounts.services.discount_notification_service import (
    DiscountNotificationEvent,
    DiscountNotificationService,
)

UserModel = get_user_model()


class DiscountMonitoringService:
    """
    Scheduled discount monitoring workflows.
    """

    @staticmethod
    def notify_expiring_discounts(*, days: int = 3) -> dict[str, int]:
        """
        Notify tenant admins about discounts expiring soon.
        """
        now = timezone.now()
        cutoff = now + timedelta(days=max(days, 1))

        discounts = Discount.objects.filter(
            is_active=True,
            is_archived=False,
            is_deleted=False,
            ends_at__isnull=False,
            ends_at__gte=now,
            ends_at__lte=cutoff,
        ).select_related("website")

        sent = 0

        for discount in discounts:
            recipients = DiscountMonitoringService._get_admin_recipients(
                website=discount.website,
            )

            for recipient in recipients:
                DiscountNotificationService.safe_notify(
                    event_key=(
                        DiscountNotificationEvent.DISCOUNT_EXPIRING_SOON
                    ),
                    recipient=recipient,
                    website=discount.website,
                    context={
                        "discount_id": discount.pk,
                        "discount_code": discount.discount_code,
                        "discount_name": discount.name,
                        "ends_at": str(discount.ends_at),
                    },
                )
                sent += 1

        return {
            "discounts_checked": discounts.count(),
            "notifications_sent": sent,
        }

    @staticmethod
    def notify_usage_limit_reached() -> dict[str, int]:
        """
        Notify tenant admins about discounts whose usage limit is reached.
        """
        discounts = (
            Discount.objects.filter(
                is_active=True,
                is_archived=False,
                is_deleted=False,
                usage_limit__isnull=False,
            )
            .annotate(usage_count=Count("usages", distinct=True))
            .filter(usage_count__gte=F("usage_limit"))
            .select_related("website")
        )

        sent = 0

        for discount in discounts:
            recipients = DiscountMonitoringService._get_admin_recipients(
                website=discount.website,
            )

            for recipient in recipients:
                DiscountNotificationService.safe_notify(
                    event_key=(
                        DiscountNotificationEvent
                        .DISCOUNT_USAGE_LIMIT_REACHED
                    ),
                    recipient=recipient,
                    website=discount.website,
                    context={
                        "discount_id": discount.pk,
                        "discount_code": discount.discount_code,
                        "usage_limit": discount.usage_limit,
                        "usage_count": getattr(discount, "usage_count", 0),
                    },
                    is_critical=True,
                )
                sent += 1

        return {
            "discounts_checked": discounts.count(),
            "notifications_sent": sent,
        }

    @staticmethod
    def _get_admin_recipients(*, website):
        """
        Return admin/superadmin users for a website.

        Adjust role field names to your accounts app if needed.
        """
        return UserModel.objects.filter(
            website=website,
            is_active=True,
            is_staff=True,
        )