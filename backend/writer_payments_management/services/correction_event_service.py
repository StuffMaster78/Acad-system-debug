from __future__ import annotations

from decimal import Decimal
from typing import Any, TypedDict

from django.utils import timezone

from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.enums.financial_event_enums import (
    FinancialEventType,
    FinancialEventStatus,
)


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
    ) -> FinancialEvent:

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

        # -----------------------------
        # CREATE IMMUTABLE EVENT
        # -----------------------------
        return FinancialEvent.objects.create(
            website=website,
            writer=writer,
            event_type=FinancialEventType.ADJUSTMENT,
            status=FinancialEventStatus.MATURED,
            amount=amount,
            title="Correction Event",
            description=reason,
            created_by=created_by,
            metadata=metadata,
        )