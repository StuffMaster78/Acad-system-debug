from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.utils import timezone

from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.models.financial_event_link_models import FinancialEventLink


class FinancialEventService:
    """
    Domain service for creating immutable financial events
    and linking them to business objects.

    RULES:
        1. FinancialEvent is immutable after creation
        2. Links are traceability metadata only
        3. No business aggregation logic here
    """

    @staticmethod
    def create_event(
        *,
        website: Any,
        writer: Any,
        event_type: str,
        amount: Decimal,
        metadata: dict | None = None,
    ) -> FinancialEvent:
        """
        Create a financial event (immutable ledger entry).
        """

        if amount is None:
            raise ValueError("amount cannot be None")

        return FinancialEvent.objects.create(
            website=website,
            writer=writer,
            event_type=event_type,
            amount=amount,
            metadata=metadata or {},
            created_at=timezone.now(),
        )

    @staticmethod
    def link_event(
        *,
        event: FinancialEvent,
        instance: Any,
        role: str,
        website: Any,
    ) -> FinancialEventLink:
        """
        Attach a financial event to a domain object for traceability.
        """

        return FinancialEventLink.objects.create(
            website=website,
            financial_event=event,
            content_type=instance.__class__.__name__,
            object_id=str(getattr(instance, "id", "")),
            event_role=role,
        )