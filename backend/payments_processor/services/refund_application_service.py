from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from ledger.models import JournalEntry
from ledger.services.reversal_ledger_service import ReversalLedgerService
from payments_processor.enums import (
    PaymentRefundStatus,
    RefundDestination,
)
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentRefund
from wallets.services.client_wallet_service import ClientWalletService
from ledger.selectors.reversal_selectors import (
    get_reversible_journal_entry_for_refund,
)


class RefundApplicationService:
    """
    Applies successful refunds internally.

    Responsibilities:
    1. reverse internal financial effects where possible
    2. credit wallet when destination is wallet
    3. keep application idempotent
    4. leave refund approval and provider execution outside this service
    """

    @classmethod
    @transaction.atomic
    def apply_refund(
        cls,
        *,
        refund: PaymentRefund,
        triggered_by: Any | None = None,
        journal_entry_to_reverse: JournalEntry | None = None,
    ) -> dict[str, Any]:
        """
        Apply a successful provider refund internally.

        Locks the PaymentRefund row with SELECT FOR UPDATE before checking
        applied_at so concurrent Celery retries cannot double-credit.
        """
        # Lock the row for the duration of this transaction.
        refund = PaymentRefund.objects.select_for_update().get(pk=refund.pk)

        cls._validate_refund_for_application(refund=refund)

        if cls._is_already_applied(refund=refund):
            return {
                "refund_id": refund.pk,
                "payment_intent_id": refund.payment_intent.pk,
                "already_applied": True,
                "destination": refund.destination,
            }

        reversal_result: dict[str, Any] | None = None

        if journal_entry_to_reverse is None:
            journal_entry_to_reverse = get_reversible_journal_entry_for_refund(
                refund=refund,
            )

        if journal_entry_to_reverse is not None:
            reversal_result = cls._reverse_financial_effects(
                refund=refund,
                journal_entry=journal_entry_to_reverse,
                triggered_by=triggered_by,
            )

        wallet_result: dict[str, Any] | None = None
        if refund.destination == RefundDestination.WALLET:
            wallet_result = cls._credit_wallet_refund(
                refund=refund,
                triggered_by=triggered_by,
            )

        cls._mark_as_applied(refund=refund)

        return {
            "refund_id": refund.pk,
            "payment_intent_id": refund.payment_intent.pk,
            "already_applied": False,
            "destination": refund.destination,
            "reversal_result": reversal_result,
            "wallet_result": wallet_result,
        }

    @staticmethod
    def _validate_refund_for_application(
        *,
        refund: PaymentRefund,
    ) -> None:
        if refund.status != PaymentRefundStatus.SUCCEEDED:
            raise PaymentError(
                f"Refund '{refund.pk}' is not internally applicable from "
                f"status '{refund.status}'."
            )

        # Bounds check — never apply more than what the PaymentIntent can refund.
        # refundable_amount = intent.amount - intent.amount_refunded.
        # This catches cases where amount_refunded was updated by a prior refund
        # (e.g., a wallet cancellation path) making this refund excess.
        payment_intent = refund.payment_intent
        refundable = payment_intent.refundable_amount
        if refund.amount > refundable:
            raise PaymentError(
                f"Refund '{refund.pk}' amount {refund.amount} exceeds the "
                f"remaining refundable amount {refundable} on intent "
                f"'{payment_intent.pk}'."
            )

    @staticmethod
    def _is_already_applied(
        *,
        refund: PaymentRefund,
    ) -> bool:
        # applied_at is the authoritative DB-level idempotency marker.
        # Fall back to the legacy metadata flag for records that predate the field.
        if refund.applied_at is not None:
            return True
        metadata = refund.metadata or {}
        return bool(metadata.get("internally_applied", False))

    @classmethod
    def _reverse_financial_effects(
        cls,
        *,
        refund: PaymentRefund,
        journal_entry: JournalEntry,
        triggered_by: Any | None = None,
    ) -> dict[str, Any]:
        """
        Reverse a posted ledger journal entry for the refund.
        """
        reversal_entry = ReversalLedgerService.reverse_entry(
            journal_entry=journal_entry,
            triggered_by=triggered_by,
            reason=(
                f"Refund reversal for payment intent "
                f"{refund.payment_intent.reference}"
            ),
            metadata={
                "payment_refund_id": refund.pk,
                "payment_intent_id": refund.payment_intent.pk,
                "provider_refund_id": refund.provider_refund_id,
            },
        )

        return {
            "reversal_entry_id": reversal_entry.pk,
            "reversal_entry_number": reversal_entry.entry_number,
        }

    @classmethod
    def _credit_wallet_refund(
        cls,
        *,
        refund: PaymentRefund,
        triggered_by: Any | None = None,
    ) -> dict[str, Any]:
        """
        Credit refund amount to the client's wallet.
        """
        payment_intent = refund.payment_intent
        client = payment_intent.client

        wallet = ClientWalletService.refund_to_wallet(
            website=refund.website,
            client=client,
            amount=refund.amount,
            created_by=triggered_by,
            description=(
                f"Refund credit for payment intent "
                f"{payment_intent.reference}"
            ),
            reference=f"refund-{refund.pk}",
            reference_type="payment_refund",
            reference_id=str(refund.pk),
            metadata={
                "payment_refund_id": refund.pk,
                "payment_intent_id": payment_intent.pk,
                "provider_refund_id": refund.provider_refund_id,
            },
        )

        return {
            "wallet_id": wallet.pk,
            "client_id": client.pk,
            "amount": str(refund.amount),
            "currency": refund.currency,
        }

    @staticmethod
    def _mark_as_applied(
        *,
        refund: PaymentRefund,
    ) -> None:
        now = timezone.now()
        # Write the DB field as the primary idempotency marker, and keep the
        # metadata flag for backwards-compatibility with older records.
        metadata = refund.metadata or {}
        metadata["internally_applied"] = True
        metadata["internally_applied_at"] = now.isoformat()

        refund.applied_at = now
        refund.metadata = metadata
        refund.save(update_fields=["applied_at", "metadata"])