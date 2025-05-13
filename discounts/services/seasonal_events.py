"""
Service for handling seasonal events and their associated discounts.
"""

import logging
from decimal import Decimal, ROUND_HALF_UP

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.utils.timezone import now

from discounts.validators import DiscountValidator
from notifications_system.services.send_notification import (
    notify_admin_of_error,
)

logger = logging.getLogger(__name__)


def get_discount_model():
    return apps.get_model('discounts', 'Discount')


def get_order_model():
    return apps.get_model('orders', 'Order')


class SeasonalEventService:
    """
    Service for handling seasonal events and their associated discounts.
    """

    @staticmethod
    def get_seasonal_event_model():
        return apps.get_model('discounts', 'SeasonalEvent')

    @classmethod
    def get_active_seasonal_events(cls, website):
        SeasonalEvent = cls.get_seasonal_event_model()
        return SeasonalEvent.objects.filter(
            website=website,
            is_active=True,
            start_date__lte=now(),
            end_date__gte=now(),
        )

    @classmethod
    def mark_expired_events(cls):
        """
        Mark all seasonal events that have expired as inactive.
        """
        SeasonalEvent = cls.get_seasonal_event_model()
        SeasonalEvent.objects.filter(
            end_date__lt=now(),
            is_active=True,
        ).update(is_active=False)

    @staticmethod
    def attach_seasonal_event_to_discount(discount, seasonal_event):
        """
        Attach a seasonal event to a discount, ensuring it aligns with the
        event's rules and timing.
        """
        if seasonal_event.is_active and seasonal_event.start_date <= now() <= seasonal_event.end_date:
            discount.seasonal_event = seasonal_event
            discount.save()
        else:
            raise ValidationError(
                "The seasonal event is not active or the discount's dates are invalid."
            )

    @staticmethod
    def get_discounts_for_event(seasonal_event):
        """
        Retrieve discounts that are part of the given seasonal event.
        """
        Discount = get_discount_model()
        return Discount.objects.filter(seasonal_event=seasonal_event)

    @staticmethod
    def is_discount_applicable(discount):
        """
        Check if the discount is linked to an active seasonal event, or
        has no event (always valid).
        """
        event = discount.seasonal_event
        if not event:
            return True
        return event.is_active and event.start_date <= now() <= event.end_date
