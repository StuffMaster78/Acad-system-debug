from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from writer_payments_management.models.payout_batch_models import PayoutBatch
from writer_payments_management.models.payout_record_models import PayoutRecord


class PayoutEngineService:
    """
    Payout intent builder.

    RULES:
        1. Batch = grouping container
        2. Record = payout intent per writer wallet
        3. Never executes money movement here
        4. Must be idempotent
    """

    STATUS_PENDING = "PENDING"

    # -----------------------------
    # CREATE BATCH
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def create_batch(
        *,
        website: Any,
        processed_by: Any | None = None,
        reference: str | None = None,
    ) -> PayoutBatch:
        """
        Create a payout batch (idempotent safe container).
        """

        batch = PayoutBatch.objects.create(
            website=website,
            processed_by=processed_by,
            status=PayoutEngineService.STATUS_PENDING,
            reference=reference,
        )

        return batch

    # -----------------------------
    # ADD RECORD
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def add_record(
        *,
        batch: PayoutBatch,
        writer_wallet: Any,
        amount: Decimal,
        reference: str | None = None,
    ) -> PayoutRecord:
        """
        Add payout intent record to batch.

        Safety rules:
            - amount must be > 0
            - no duplicate wallet entry per batch
        """

        if amount <= Decimal("0.00"):
            raise ValueError("Payout amount must be greater than zero")

        # Prevent duplicate payouts for same wallet in same batch
        existing = PayoutRecord.objects.filter(
            batch=batch,
            writer_wallet=writer_wallet,
        ).first()

        if existing:
            return existing

        return PayoutRecord.objects.create(
            batch=batch,
            writer_wallet=writer_wallet,
            amount=amount,
            status=PayoutEngineService.STATUS_PENDING,
            reference=reference,
        )