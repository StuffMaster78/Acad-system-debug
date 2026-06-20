from __future__ import annotations

from decimal import Decimal
from typing import Any, TypedDict

from django.utils import timezone

from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.enums.compensation_enums import (
    EventStatus,
    EventType,
)
from writer_compensation.services.event_intake_service import EventIntakeService


# -----------------------------
# STRICT METADATA CONTRACT
# -----------------------------
class CorrectionMetadata(TypedDict, total=False):
    system: str
    source: str
    correction_type: str
    generated_at: str
    idempotency_key: str
    related_object_id: int | None
    related_object_type: str


class CorrectionEventService:
    """
    Append-only correction event generator.

    HARD RULES:
        1. Never mutate historical financial data
        2. Always emit compensating FinancialEvent
        3. Always idempotent-safe via metadata keys
        4. Never use dynamic or untyped metadata blobs
    """

    @staticmethod
    def create_correction(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        correction_type: str = "SYSTEM_CORRECTION",
        source: str = "LEDGER_SYNC",
        related_object: Any | None = None,
        created_by: Any | None = None,
        idempotency_key: str | None = None,
    ) -> CompensationEvent:

        # -----------------------------
        # HARD SAFETY GUARD
        # -----------------------------
        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal")

        if amount == Decimal("0.00"):
            raise ValueError("Correction amount cannot be zero")

        # -----------------------------
        # BUILD SAFE METADATA
        # -----------------------------
        metadata: CorrectionMetadata = {
            "system": "correction_event",
            "source": source,
            "correction_type": correction_type,
            "generated_at": timezone.now().isoformat(),
        }

        if idempotency_key is not None:
            metadata["idempotency_key"] = idempotency_key

        if related_object is not None:
            metadata["related_object_id"] = getattr(related_object, "id", None)
            metadata["related_object_type"] = related_object.__class__.__name__

        # -----------------------------
        # FINAL SAFETY CHECK (anti-bug shield)
        # -----------------------------
        if callable(metadata):
            raise RuntimeError("metadata became callable (shadowing bug detected)")

        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dict")

        # Route through EventIntakeService so the event gets a payment_window
        # (direct objects.create() would raise IntegrityError on the non-nullable FK).
        event, _ = EventIntakeService.record(
            website=website,
            writer=writer,
            event_type=EventType.ADJUSTMENT,
            amount=amount,
            title="Correction Event",
            notes=reason,
            idempotency_key=idempotency_key or "",
            created_by=created_by,
        )

        # Mature immediately and attach metadata — corrections are pre-approved.
        event.status = EventStatus.MATURED
        event.metadata = metadata
        event.save(update_fields=["status", "metadata"])

        return event