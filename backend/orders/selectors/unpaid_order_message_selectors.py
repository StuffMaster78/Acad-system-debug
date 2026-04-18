from __future__ import annotations

from django.db.models import QuerySet

from orders.models.legacy_models.unpaid_order_message import UnpaidOrderMessage
from websites.models.websites import Website


class UnpaidOrderMessageSelector:
    """
    Read only queries for unpaid order message configuration.
    """

    @staticmethod
    def get_active_messages_for_website(
        *,
        website: Website,
    ) -> QuerySet[UnpaidOrderMessage]:
        """
        Return active reminder messages for a website in execution order.
        """
        return UnpaidOrderMessage.objects.filter(
            website=website,
            is_active=True,
        ).order_by("sequence_number", "interval_hours", "id")

    @staticmethod
    def get_messages_for_website(
        *,
        website: Website,
    ) -> QuerySet[UnpaidOrderMessage]:
        """
        Return all reminder messages for a website in execution order.
        """
        return UnpaidOrderMessage.objects.filter(
            website=website,
        ).order_by("sequence_number", "interval_hours", "id")