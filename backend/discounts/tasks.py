from __future__ import annotations

from celery import shared_task

from discounts.services.campaign_scheduler_service import (
    CampaignSchedulerService,
)
from discounts.services.discount_monitoring_service import (
    DiscountMonitoringService,
)


@shared_task(name="discounts.activate_and_expire_campaigns")
def activate_and_expire_campaigns() -> dict[str, int]:
    """
    Activate due campaigns and deactivate expired campaigns.
    """
    return CampaignSchedulerService.run()


@shared_task(name="discounts.notify_expiring_discounts")
def notify_expiring_discounts(*, days: int = 3) -> dict[str, int]:
    """
    Notify admins about discounts expiring soon.
    """
    return DiscountMonitoringService.notify_expiring_discounts(
        days=days,
    )


@shared_task(name="discounts.notify_usage_limit_reached")
def notify_usage_limit_reached() -> dict[str, int]:
    """
    Notify admins about discounts whose usage limit is reached.
    """
    return DiscountMonitoringService.notify_usage_limit_reached()