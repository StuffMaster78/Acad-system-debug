from __future__ import annotations

from django.utils import timezone

from payments_processor.enums import PaymentIntentStatus
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentIntent
from payments_processor.enums import PaymentApplicationStatus


class PaymentApplicationGuardService:
    """
    Ensures payments are applied internally only once and safely.
    """

    @staticmethod
    def can_apply(payment_intent: PaymentIntent) -> bool:
        """
        Check if payment is eligible for application.
        """
        if payment_intent.status != PaymentIntentStatus.SUCCEEDED:
            return False

        if (
            payment_intent.application_status
            == PaymentApplicationStatus.APPLIED
        ):
            return False

        return True

    @staticmethod
    def mark_as_applied(
        payment_intent: PaymentIntent,
    ) -> PaymentIntent:
        """
        Mark payment as applied.
        """
        if (
            payment_intent.application_status
            == PaymentApplicationStatus.APPLIED
        ):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' already applied."
            )

        payment_intent.application_status = (
            PaymentApplicationStatus.APPLIED
        )
        payment_intent.application_error = ""
        payment_intent.save(
            update_fields=[
                "application_status",
                "application_error",
                "updated_at",
            ]
        )

        return payment_intent

    @staticmethod
    def mark_as_failed(
        *,
        payment_intent: PaymentIntent,
        error: str,
    ) -> None:
        """
        Mark application as failed.
        """
        payment_intent.application_status = (
            PaymentApplicationStatus.APPLICATION_FAILED
        )
        payment_intent.application_error = error
        payment_intent.save(
            update_fields=[
                "application_status",
                "application_error",
                "updated_at",
            ]
        )