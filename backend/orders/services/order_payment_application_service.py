from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models.orders.enums import (
    OrderPaymentStatus,
    OrderStatus,
)
from orders.models.orders.order import Order
from orders.models.orders.order_timeline_event import (
    OrderTimelineEvent,
)
from payments_processor.services.payment_intent_service import (
    PaymentIntentService,
)
from orders.services.order_discount_integration_service import (
    OrderDiscountIntegrationService,
)

class OrderPaymentApplicationService:
    """
    Bridge order funding workflow to payments_processor.

    Responsibilities:
        1. Create external payment intents for orders.
        2. Apply confirmed payment results to the order.
        3. Support split funding state updates.
        4. Move fully funded orders into staffing readiness.
        5. Record timeline events for payment transitions.
    """

    TIMELINE_EVENT_PAYMENT_INITIATED = "payment_initiated"
    TIMELINE_EVENT_PAYMENT_APPLIED = "payment_applied"
    TIMELINE_EVENT_ORDER_FULLY_FUNDED = "order_fully_funded"

    @classmethod
    @transaction.atomic
    def start_checkout(
        cls,
        *,
        order: Order,
        provider: str,
        purpose: str = "order_payment",
        triggered_by: Optional[Any] = None,
        payment_method_code: str = "",
        metadata: Optional[dict[str, Any]] = None,
        entered_code: Optional[str] = None,
        lifetime_spend: Optional[Decimal] = None,
        has_prior_paid_purchase: bool = False,
    ) -> Any:
        """
        Create an external payment intent for the current outstanding
        order balance.

        When entered_code or lifetime_spend are provided, the discount
        engine resolves and applies the best discount before the payment
        intent amount is calculated.
        """
        cls._validate_order_for_checkout(order=order)

        # Apply discount if a code was entered or spend data is available.
        discount_metadata: dict = {}
        if entered_code or lifetime_spend is not None:
            try:
                discount_result = OrderDiscountIntegrationService.apply_order_discount(
                    order=order,
                    entered_code=entered_code,
                    lifetime_spend=lifetime_spend,
                    has_prior_paid_purchase=has_prior_paid_purchase,
                )
                if discount_result is not None:
                    discount_metadata = {
                        "discount_code": getattr(discount_result, "discount_code", ""),
                        "discount_amount": str(
                            getattr(discount_result, "discount_amount", "0.00")
                        ),
                    }
            except Exception:
                import logging
                logging.getLogger(__name__).warning(
                    "Discount application failed for order=%s; proceeding without discount.",
                    order.pk,
                    exc_info=True,
                )

        amount_to_charge = cls.get_outstanding_amount(order=order)
        if amount_to_charge <= Decimal("0.00"):
            raise ValidationError(
                {"order": "Order does not require external payment."}
            )

        payment_intent = PaymentIntentService.create_intent(
            client=order.client,
            provider=provider,
            purpose=purpose,
            amount=amount_to_charge,
            currency=order.currency,
            payable=order,
            metadata={
                "order_id": order.pk,
                "service_family": order.service_family,
                "service_code": order.service_code,
                **discount_metadata,
                **(metadata or {}),
            },
            reference_prefix=f"order_{order.pk}",
            website=order.website,
        )

        if order.status != OrderStatus.PENDING_PAYMENT:
            order.status = OrderStatus.PENDING_PAYMENT
        order.save(update_fields=["status", "updated_at"])

        cls._create_timeline_event(
            order=order,
            actor=triggered_by,
            event_type=cls.TIMELINE_EVENT_PAYMENT_INITIATED,
            metadata={
                "payment_intent_reference": getattr(
                    payment_intent,
                    "reference",
                    "",
                ),
                "amount": str(amount_to_charge),
                "provider": provider,
                **discount_metadata,
            },
        )

        return payment_intent

    @classmethod
    @transaction.atomic
    def apply_confirmed_payment(
        cls,
        *,
        order: Order,
        amount: Decimal,
        payment_reference: str,
        triggered_by: Optional[Any] = None,
        payment_intent_reference: str = "",
        source: str = "external",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Order:
        """
        Apply a confirmed payment outcome to the order.

        This method should be called only after the wallet or external
        processor has already confirmed the money movement.
        """
        cls._validate_payment_amount(amount=amount)

        locked_order = cls._lock_order(order)

        current_paid_amount = locked_order.amount_paid
        new_paid_amount = current_paid_amount + amount
        if new_paid_amount > locked_order.total_price:
            raise ValidationError(
                {"amount": "Payment would overfund the order."}
            )

        locked_order.amount_paid = new_paid_amount

        if cls._is_fully_funded(
            order=locked_order,
            paid_amount=new_paid_amount,
        ):
            locked_order.payment_status = OrderPaymentStatus.FULLY_PAID
            locked_order.status = OrderStatus.READY_FOR_STAFFING
        elif new_paid_amount > Decimal("0.00"):
            locked_order.payment_status = (
                OrderPaymentStatus.PARTIALLY_PAID
            )
            locked_order.status = OrderStatus.PENDING_PAYMENT
        else:
            locked_order.payment_status = OrderPaymentStatus.UNPAID
            locked_order.status = OrderStatus.PENDING_PAYMENT

        locked_order.save(
            update_fields=[
                "amount_paid",
                "payment_status",
                "status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            actor=triggered_by,
            event_type=cls.TIMELINE_EVENT_PAYMENT_APPLIED,
            metadata={
                "payment_reference": payment_reference,
                "payment_intent_reference": payment_intent_reference,
                "amount": str(amount),
                "new_paid_amount": str(new_paid_amount),
                "source": source,
                **(metadata or {}),
            },
        )

        if cls._is_fully_funded(
            order=locked_order,
            paid_amount=new_paid_amount,
        ):
            cls._create_timeline_event(
                order=locked_order,
                actor=triggered_by,
                event_type=cls.TIMELINE_EVENT_ORDER_FULLY_FUNDED,
                metadata={
                    "total_price": str(locked_order.total_price),
                    "paid_amount": str(new_paid_amount),
                },
            )

        return locked_order

    @classmethod
    @transaction.atomic
    def apply_split_payment_summary(
        cls,
        *,
        order: Order,
        wallet_amount: Decimal,
        external_amount: Decimal,
        payment_reference: str,
        triggered_by: Optional[Any] = None,
        payment_intent_reference: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Order:
        """
        Apply the combined result of wallet and external funding to the
        order aggregate after both parts are confirmed elsewhere.
        """
        if wallet_amount < Decimal("0.00") or external_amount < Decimal(
            "0.00"
        ):
            raise ValidationError(
                {"amount": "Split payment amounts cannot be negative."}
            )

        total_amount = wallet_amount + external_amount
        if total_amount <= Decimal("0.00"):
            raise ValidationError(
                {
                    "amount": (
                        "At least one split payment amount must be "
                        "greater than zero."
                    )
                }
            )

        return cls.apply_confirmed_payment(
            order=order,
            amount=total_amount,
            payment_reference=payment_reference,
            triggered_by=triggered_by,
            payment_intent_reference=payment_intent_reference,
            source="split",
            metadata={
                "wallet_amount": str(wallet_amount),
                "external_amount": str(external_amount),
                **(metadata or {}),
            },
        )

    @staticmethod
    def get_outstanding_amount(*, order: Order) -> Decimal:
        """
        Return the remaining amount to charge.
        """
        outstanding = order.total_price - order.amount_paid
        if outstanding < Decimal("0.00"):
            return Decimal("0.00")
        return outstanding

    @staticmethod
    def _validate_order_for_checkout(*, order: Order) -> None:
        if order.total_price <= Decimal("0.00"):
            raise ValidationError(
                {"order": "Order total price must be greater than zero."}
            )

        if getattr(order, "archived_at", None) is not None:
            raise ValidationError(
                {"order": "Archived orders cannot enter checkout."}
            )

    @staticmethod
    def _validate_payment_amount(*, amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise ValidationError(
                {"amount": "Payment amount must be greater than zero."}
            )

    @staticmethod
    def _is_fully_funded(
        *,
        order: Order,
        paid_amount: Decimal,
    ) -> bool:
        return paid_amount >= order.total_price

    @staticmethod
    def _lock_order(order: Order) -> Order:
        return Order.objects.select_for_update().get(pk=order.pk)

    @staticmethod
    def _create_timeline_event(
        *,
        order: Order,
        actor: Optional[Any],
        event_type: str,
        metadata: dict[str, Any],
    ) -> OrderTimelineEvent:
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )