from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from discounts.services.discount_usage_tracker import DiscountUsageTracker
from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.enums import OrderPaymentStatus, OrderStatus
from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentRefundStatus,
    RefundDestination,
)
from payments_processor.services.refund_execution_service import (
    RefundExecutionService,
)
from refunds.models import Refund, RefundLog, RefundReceipt
from wallets.services.client_wallet_service import ClientWalletService


class RefundProcessorService:
    """
    Orchestrate client refund workflows.

    The service keeps business approval and audit state in refunds while
    delegating money movement to the canonical apps:
    wallets for wallet credits and payments_processor for provider refunds.
    """

    @classmethod
    @transaction.atomic
    def process_refund(
        cls,
        *,
        refund: Refund,
        processed_by: Any | None,
        reason: str | None = None,
        admin_user: Any | None = None,
    ) -> Refund:
        """Process a pending refund to wallet, original method, or both."""
        locked_refund = (
            Refund.objects.select_for_update()
            .select_related("order_payment", "client", "website", "order")
            .get(pk=refund.pk)
        )
        payment = locked_refund.order_payment

        cls._validate_refund(refund=locked_refund)

        if locked_refund.wallet_amount > Decimal("0.00"):
            cls._process_wallet_refund(
                refund=locked_refund,
                processed_by=processed_by,
            )

        if locked_refund.external_amount > Decimal("0.00"):
            payment_refund = cls._process_external_refund(
                refund=locked_refund,
            )
            locked_refund.payment_refund = payment_refund

        locked_refund.status = Refund.PROCESSED
        locked_refund.processed_by = processed_by
        locked_refund.processed_at = timezone.now()
        locked_refund.reason = reason or locked_refund.reason
        locked_refund.error_message = ""
        locked_refund.save(
            update_fields=[
                "payment_refund",
                "status",
                "processed_by",
                "processed_at",
                "reason",
                "error_message",
                "updated_at",
            ]
        )

        cls._generate_receipt(
            refund=locked_refund,
            processed_by=processed_by,
            reason=reason,
        )
        cls._log_refund(
            refund=locked_refund,
            processed_by=processed_by,
            action="Refund Processed",
            source=locked_refund.refund_method,
            status=locked_refund.status,
            metadata={"reason": reason or locked_refund.reason},
        )
        cls._handle_full_refund_side_effects(
            refund=locked_refund,
            processed_by=processed_by,
            reason=reason,
        )
        cls._notify_client(
            refund=locked_refund,
            processed_by=processed_by,
            reason=reason,
        )

        payment.refresh_from_db()
        locked_refund.refresh_from_db()
        return locked_refund

    @classmethod
    @transaction.atomic
    def reject_refund(
        cls,
        *,
        refund: Refund,
        processed_by: Any | None,
        reason: str,
    ) -> Refund:
        """Reject or cancel a pending refund request."""
        locked_refund = Refund.objects.select_for_update().get(pk=refund.pk)
        if locked_refund.status != Refund.PENDING:
            raise ValidationError("Only pending refunds can be canceled.")

        locked_refund.status = Refund.REJECTED
        locked_refund.error_message = reason
        locked_refund.processed_by = processed_by
        locked_refund.processed_at = timezone.now()
        locked_refund.save(
            update_fields=[
                "status",
                "error_message",
                "processed_by",
                "processed_at",
                "updated_at",
            ]
        )
        cls._log_refund(
            refund=locked_refund,
            processed_by=processed_by,
            action="Refund Canceled",
            source="manual",
            status=locked_refund.status,
            metadata={"reason": reason},
        )
        return locked_refund

    @classmethod
    def create_for_payment(
        cls,
        *,
        payment_intent: Any,
        wallet_amount: Decimal = Decimal("0.00"),
        external_amount: Decimal = Decimal("0.00"),
        requested_by: Any | None = None,
        refund_type: str = Refund.AUTOMATED,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Refund:
        """
        Create a refund request for a payment intent.

        This is the entry point order cancellation and dispute workflows
        should call after deciding the refund amounts.
        """
        refund = Refund(
            order_payment=payment_intent,
            wallet_amount=wallet_amount,
            external_amount=external_amount,
            client=getattr(payment_intent, "client", None),
            website=getattr(payment_intent, "website", None),
            type=refund_type,
            reason=reason,
            metadata={
                "requested_by_id": getattr(requested_by, "pk", None),
                **(metadata or {}),
            },
        )
        refund.full_clean()
        refund.save()
        return refund

    @staticmethod
    def refundable_amount(*, payment_intent: Any) -> Decimal:
        """Return remaining amount not already refunded or pending."""
        reserved = (
            Refund.objects.filter(
                order_payment=payment_intent,
                status=Refund.PENDING,
            )
            .aggregate(
                wallet_total=Sum("wallet_amount"),
                external_total=Sum("external_amount"),
            )
        )
        wallet_total = reserved["wallet_total"] or Decimal("0.00")
        external_total = reserved["external_total"] or Decimal("0.00")
        remaining = (
            payment_intent.amount
            - payment_intent.amount_refunded
            - wallet_total
            - external_total
        )
        return max(remaining, Decimal("0.00"))

    @classmethod
    def _validate_refund(cls, *, refund: Refund) -> None:
        if refund.status != Refund.PENDING:
            raise ValidationError("Refund has already been processed.")

        refund.full_clean()

        payment = refund.order_payment
        if payment.status not in {
            PaymentIntentStatus.SUCCEEDED,
            PaymentIntentStatus.PARTIALLY_REFUNDED,
        }:
            raise ValidationError("Payment is not refundable.")

        other_reserved = (
            Refund.objects.filter(order_payment=payment)
            .exclude(pk=refund.pk)
            .filter(status=Refund.PENDING)
            .aggregate(
                wallet_total=Sum("wallet_amount"),
                external_total=Sum("external_amount"),
            )
        )
        wallet_total = other_reserved["wallet_total"] or Decimal("0.00")
        external_total = other_reserved["external_total"] or Decimal("0.00")
        refundable = (
            payment.amount
            - payment.amount_refunded
            - wallet_total
            - external_total
        )

        if refund.total_amount() > refundable:
            raise ValidationError("Refund exceeds refundable balance.")

    @classmethod
    def _process_wallet_refund(
        cls,
        *,
        refund: Refund,
        processed_by: Any | None,
    ) -> None:
        ClientWalletService.refund_to_wallet(
            website=refund.website,
            client=refund.client,
            amount=refund.wallet_amount,
            created_by=processed_by,
            description=(
                f"Refund for payment {refund.order_payment.reference}"
            ),
            reference=f"refund-{refund.pk}",
            reference_type="refund",
            reference_id=str(refund.pk),
            metadata={
                "refund_id": refund.pk,
                "payment_intent_id": refund.order_payment.pk,
                "order_id": refund.order.pk if refund.order else None,
            },
        )
        cls._update_payment_refund_state(
            payment_intent=refund.order_payment,
            amount=refund.wallet_amount,
        )

    @staticmethod
    def _process_external_refund(*, refund: Refund):
        result = RefundExecutionService.execute_refund(
            payment_intent=refund.order_payment,
            amount=refund.external_amount,
            destination=RefundDestination.ORIGINAL_METHOD,
            metadata={
                "refund_workflow_id": refund.pk,
                "order_id": refund.order.pk if refund.order else None,
            },
        )
        payment_refund = result["refund"]
        if payment_refund.status == PaymentRefundStatus.FAILED:
            raise ValidationError(
                payment_refund.failure_message or "External refund failed."
            )
        return payment_refund

    @staticmethod
    def _update_payment_refund_state(
        *,
        payment_intent: Any,
        amount: Decimal,
    ) -> None:
        payment_intent.amount_refunded += amount
        if payment_intent.amount_refunded >= payment_intent.amount:
            payment_intent.status = PaymentIntentStatus.REFUNDED
        else:
            payment_intent.status = PaymentIntentStatus.PARTIALLY_REFUNDED
        payment_intent.save(
            update_fields=["amount_refunded", "status", "updated_at"]
        )

    @staticmethod
    def _generate_receipt(
        *,
        refund: Refund,
        processed_by: Any | None,
        reason: str | None,
    ) -> None:
        RefundReceipt.objects.get_or_create(
            refund=refund,
            defaults={
                "amount": refund.total_amount(),
                "processed_by": processed_by,
                "website": refund.website,
                "order_payment": refund.order_payment,
                "client": refund.client,
                "reason": reason or refund.reason,
            },
        )

    @staticmethod
    def _log_refund(
        *,
        refund: Refund,
        processed_by: Any | None,
        action: str,
        source: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        RefundLog.objects.create(
            website=refund.website,
            order=refund.order,
            refund=refund,
            client=refund.client,
            processed_by=processed_by,
            action=action,
            amount=refund.total_amount(),
            source=source,
            status=status,
            metadata=metadata or {},
        )

    @classmethod
    def _handle_full_refund_side_effects(
        cls,
        *,
        refund: Refund,
        processed_by: Any | None,
        reason: str | None,
    ) -> None:
        if not refund.is_full_refund:
            return

        order = refund.order
        if order is None:
            return

        order.status = OrderStatus.REFUNDED
        order.payment_status = OrderPaymentStatus.REFUNDED
        order.cancelled_at = order.cancelled_at or timezone.now()
        order.cancelled_by = processed_by
        order.cancellation_reason = reason or refund.reason
        order.save(
            update_fields=[
                "status",
                "payment_status",
                "cancelled_at",
                "cancelled_by",
                "cancellation_reason",
                "updated_at",
            ]
        )

        try:
            DiscountUsageTracker.untrack(order)
        except Exception:
            pass

    @staticmethod
    def _notify_client(
        *,
        refund: Refund,
        processed_by: Any | None,
        reason: str | None,
    ) -> None:
        try:
            NotificationService.notify(
                event_key="wallet.refund_completed",
                recipient=refund.client,
                website=refund.website,
                context={
                    "refund_id": refund.pk,
                    "order_id": refund.order.pk if refund.order else None,
                    "amount": str(refund.total_amount()),
                    "wallet_amount": str(refund.wallet_amount),
                    "external_amount": str(refund.external_amount),
                    "reason": reason or refund.reason,
                    "performed_by_id": (
                        processed_by.pk if processed_by else None
                    ),
                },
            )
        except Exception:
            pass
