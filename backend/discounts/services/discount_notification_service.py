from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from notifications_system.services.notification_service import (
    NotificationService,
)

logger = logging.getLogger(__name__)


class DiscountNotificationEvent:
    """
    Notification event keys for discount workflows.
    """

    DISCOUNT_APPLIED = "discount.applied"
    DISCOUNT_EXPIRING_SOON = "discount.expiring_soon"
    DISCOUNT_USAGE_LIMIT_REACHED = "discount.usage_limit_reached"

    CAMPAIGN_ACTIVATED = "discount.campaign_activated"
    CAMPAIGN_DEACTIVATED = "discount.campaign_deactivated"
    CAMPAIGN_ARCHIVED = "discount.campaign_archived"
    CAMPAIGN_RESTORED = "discount.campaign_restored"

    TIER_CREATED = "discount.tier_created"
    LOYALTY_CREATED = "discount.loyalty_created"


class DiscountNotificationService:
    """
    Dispatch discount notifications through the central notification system.

    Notification failures must not break checkout, campaign scheduling,
    or admin operations.
    """

    @staticmethod
    def safe_notify(
        *,
        event_key: str,
        recipient,
        website,
        context: dict[str, Any],
        triggered_by=None,
        is_critical: bool = False,
        is_silent: bool = False,
    ):
        """
        Send notification without breaking the caller.
        """
        try:
            return NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
                triggered_by=triggered_by,
                is_critical=is_critical,
                is_silent=is_silent,
            )
        except Exception:
            logger.exception(
                "Discount notification failed: %s",
                event_key,
            )
            return None

    @classmethod
    def notify_discount_applied(cls, *, usage) -> None:
        """
        Notify client that discount was applied.
        """
        cls.safe_notify(
            event_key=DiscountNotificationEvent.DISCOUNT_APPLIED,
            recipient=usage.client,
            website=usage.website,
            context={
                "discount_code": usage.discount_code,
                "payable_type": usage.payable_type,
                "payable_id": usage.payable_id,
                "subtotal_amount": str(usage.subtotal_amount),
                "discount_amount": str(usage.discount_amount),
                "final_amount": str(usage.final_amount),
            },
            triggered_by=usage.client,
            is_silent=True,
        )

    @classmethod
    def notify_campaign_event(
        cls,
        *,
        campaign,
        event_key: str,
        recipient,
        triggered_by=None,
    ) -> None:
        """
        Notify staff/admin about campaign lifecycle events.
        """
        cls.safe_notify(
            event_key=event_key,
            recipient=recipient,
            website=campaign.website,
            context={
                "campaign_id": campaign.pk,
                "campaign_name": campaign.name,
                "starts_at": str(campaign.starts_at or ""),
                "ends_at": str(campaign.ends_at or ""),
            },
            triggered_by=triggered_by,
        )

    @classmethod
    def notify_tier_created(
        cls,
        *,
        tier,
        recipient,
        triggered_by=None,
    ) -> None:
        """
        Notify staff/admin that a spend tier was created.
        """
        cls.safe_notify(
            event_key=DiscountNotificationEvent.TIER_CREATED,
            recipient=recipient,
            website=tier.website,
            context={
                "tier_id": tier.pk,
                "tier_name": tier.name,
                "discount_code": tier.discount.discount_code,
                "minimum_lifetime_spend": (
                    str(tier.minimum_lifetime_spend)
                ),
            },
            triggered_by=triggered_by,
        )

    @classmethod
    def notify_large_discount_applied(
        cls,
        *,
        usage,
        recipient,
        threshold: Decimal,
    ) -> None:
        """
        Notify staff/admin when a large discount is applied.
        """
        cls.safe_notify(
            event_key=DiscountNotificationEvent.DISCOUNT_APPLIED,
            recipient=recipient,
            website=usage.website,
            context={
                "discount_code": usage.discount_code,
                "discount_amount": str(usage.discount_amount),
                "threshold": str(threshold),
                "client_id": usage.client_id,
                "payable_type": usage.payable_type,
                "payable_id": usage.payable_id,
            },
            is_critical=True,
        )