from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from discounts.models import Discount, DiscountUsage, SeasonalEvent
from discounts.validators import DiscountValidator
from django.db.models import F
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from notifications_system.services.send_notification import (
    notify_admin_of_error
)
from users.models import User
from orders.models import Order
import logging


class SeasonalEventService:
    """
    Service for handling seasonal events and their associated discounts.
    """
    
    @staticmethod
    def get_active_seasonal_events(website):
        return SeasonalEvent.objects.filter(
            website=website,
            is_active=True,
            start_date__lte=now(),
            end_date__gte=now()
        )
    
    @staticmethod
    def mark_expired_events():
        """
        Mark all seasonal events that have expired as inactive.
        """
        SeasonalEvent.objects.filter(
            end_date__lt=now(),
            is_active=True
        ).update(is_active=False)

    @staticmethod
    def attach_seasonal_event_to_discount(discount, seasonal_event):
        """
        Attach a seasonal event to a discount, ensuring it aligns with the event's
        rules and timing.
        """
        if seasonal_event.is_active:
            if seasonal_event.start_date <= now() <= seasonal_event.end_date:
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
        return Discount.objects.filter(seasonal_event=seasonal_event)
    
    @staticmethod
    def is_discount_applicable(discount):
        """
        Check if the discount is linked to an active seasonal event, or
        has no event (always valid).
        """
        event = discount.seasonal_event
        if not event:
            return True  # Not seasonal — valid year-round

        return event.is_active and event.start_date <= now() <= event.end_date