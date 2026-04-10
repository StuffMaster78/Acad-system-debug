from __future__ import annotations

from django.utils import timezone

from payments_processor.enums import PaymentIntentStatus
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentIntent


class PaymentApplicationGuardService:
    """
    Ensures payments are applied internally only once and safely.
    """

    @staticmethod
    def can_apply(payment_intent: PaymentIntent) -> bool:
        """
        Check if a payment is eligible for internal application.
        """
        if payment_intent.status != PaymentIntentStatus.SUCCEEDED:
            return False

        if payment_intent.metadata.get("applied", False):
            return False

        return True

    @staticmethod
    def mark_as_applied(payment_intent: PaymentIntent) -> PaymentIntent:
        """
        Mark payment as applied internally.
        """
        if payment_intent.metadata.get("applied", False):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' already applied."
            )

        metadata = payment_intent.metadata or {}
        metadata["applied"] = True
        metadata["applied_at"] = timezone.now().isoformat()

        payment_intent.metadata = metadata
        payment_intent.save(update_fields=["metadata", "updated_at"])

        return payment_intent

    @staticmethod
    def ensure_not_applied(payment_intent: PaymentIntent) -> None:
        """
        Raise if payment already applied.
        """
        if payment_intent.metadata.get("applied", False):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' already applied."
            )