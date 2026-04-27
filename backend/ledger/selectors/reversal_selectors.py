from __future__ import annotations

from typing import Optional

from ledger.constants import JournalEntryStatus
from ledger.models import JournalEntry
from payments_processor.models import PaymentIntent, PaymentRefund


def get_posted_journal_entry_by_payment_intent_reference(
    *,
    payment_intent_reference: str,
) -> Optional[JournalEntry]:
    """
    Return the most recent posted journal entry for a payment intent
    reference.

    This is the safest direct lookup when the original payment posting
    stored the payment intent reference on the journal entry.
    """
    return (
        JournalEntry.objects.filter(
            payment_intent_reference=payment_intent_reference,
            status=JournalEntryStatus.POSTED,
        )
        .order_by("-created_at")
        .first()
    )


def get_posted_journal_entry_by_reference(
    *,
    reference: str,
) -> Optional[JournalEntry]:
    """
    Return the most recent posted journal entry by generic reference.
    """
    return (
        JournalEntry.objects.filter(
            reference=reference,
            status=JournalEntryStatus.POSTED,
        )
        .order_by("-created_at")
        .first()
    )


def get_posted_journal_entry_by_source_object_id(
    *,
    source_object_id: str,
) -> Optional[JournalEntry]:
    """
    Return the most recent posted journal entry by source object ID.

    This is a weaker fallback than payment_intent_reference because source
    object IDs may be reused across domains depending on your setup.
    """
    return (
        JournalEntry.objects.filter(
            source_object_id=source_object_id,
            status=JournalEntryStatus.POSTED,
        )
        .order_by("-created_at")
        .first()
    )


def get_reversible_journal_entry_for_payment_intent(
    *,
    payment_intent: PaymentIntent,
) -> Optional[JournalEntry]:
    """
    Resolve the best posted journal entry to reverse for a payment intent.

    Lookup order:
    1. payment_intent_reference
    2. generic reference
    3. source_object_id fallback
    """
    entry = get_posted_journal_entry_by_payment_intent_reference(
        payment_intent_reference=payment_intent.reference,
    )
    if entry is not None:
        return entry

    entry = get_posted_journal_entry_by_reference(
        reference=payment_intent.reference,
    )
    if entry is not None:
        return entry

    if payment_intent.pk is None:
        return None

    return get_posted_journal_entry_by_source_object_id(
        source_object_id=str(payment_intent.pk),
    )


def get_reversible_journal_entry_for_refund(
    *,
    refund: PaymentRefund,
) -> Optional[JournalEntry]:
    """
    Resolve the best posted journal entry to reverse for a refund.

    Refunds usually reverse the original payment-side journal entry, not a
    refund journal entry. So this delegates to the linked payment intent.
    """
    return get_reversible_journal_entry_for_payment_intent(
        payment_intent=refund.payment_intent,
    )