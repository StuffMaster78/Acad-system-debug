from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils import timezone

from writer_compensation.models.financial_event_models import FinancialEvent
from writer_compensation.enums.financial_event_enums import (
    FinancialEventType,
    FinancialEventStatus,
)


class FinancialEventFactory:
    """
    Single entry point for ALL financial event creation.

    This enforces:
        1. type safety
        2. metadata consistency
        3. idempotency support
        4. audit-ready structure
        5. deterministic financial behavior
    """

    # -----------------------------
    # PUBLIC ENTRY
    # -----------------------------
    @staticmethod
    def create(
        *,
        website: Any,
        writer: Any,
        event_type: FinancialEventType,
        amount: Decimal,
        title: str,
        description: str = "",
        status: FinancialEventStatus = FinancialEventStatus.MATURED,
        created_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FinancialEvent:

        FinancialEventFactory._validate_amount(amount)
        FinancialEventFactory._validate_event_type(event_type)

        safe_metadata = FinancialEventFactory._normalize_metadata(metadata)

        return FinancialEvent.objects.create(
            website=website,
            writer=writer,
            event_type=event_type,
            status=status,
            amount=amount,
            title=title,
            description=description,
            created_by=created_by,
            metadata=safe_metadata,
        )

    # -----------------------------
    # CORRECTION SHORTCUT
    # -----------------------------
    @staticmethod
    def create_correction(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        created_by: Any | None = None,
        source: str = "FACTORY_CORRECTION",
        idempotency_key: str | None = None,
    ) -> FinancialEvent:

        metadata = {
            "system": "financial_factory",
            "type": "correction",
            "source": source,
            "generated_at": timezone.now().isoformat(),
        }

        if idempotency_key:
            metadata["idempotency_key"] = idempotency_key

        return FinancialEventFactory.create(
            website=website,
            writer=writer,
            event_type=FinancialEventType.ADJUSTMENT,
            amount=amount,
            title="Correction Event",
            description=reason,
            created_by=created_by,
            metadata=metadata,
        )

    # -----------------------------
    # VALIDATION LAYER
    # -----------------------------
    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal")

        if amount == Decimal("0.00"):
            raise ValueError("amount cannot be zero")

    @staticmethod
    def _validate_event_type(event_type: FinancialEventType) -> None:
        if event_type not in FinancialEventType.values:
            raise ValueError(f"invalid event type: {event_type}")

    # -----------------------------
    # METADATA HARDENING
    # -----------------------------
    @staticmethod
    def _normalize_metadata(
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:

        safe = dict(metadata or {})

        # prevent weird runtime poisoning
        if callable(safe):
            raise RuntimeError("metadata cannot be callable")

        # enforce string safety for JSON fields
        for k, v in list(safe.items()):
            if v is None:
                safe[k] = ""
            elif isinstance(v, (dict, list)):
                # keep JSON-safe but stable
                safe[k] = v
            else:
                safe[k] = str(v)

        safe["factory_timestamp"] = timezone.now().isoformat()

        return safe