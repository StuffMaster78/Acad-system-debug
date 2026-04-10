from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from payments_processor.enums import PaymentIntentPurpose
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentIntent
from payments_processor.services.payment_allocation_application_service import (
    PaymentAllocationApplicationService,
)
from payments_processor.services.payment_application_guard_service import (
    PaymentApplicationGuardService,
)


class PaymentApplicationService:
    """
    Applies successful payments internally in an idempotent and
    settlement-aware manner.
    """

    @classmethod
    @transaction.atomic
    def apply_payment(
        cls,
        *,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> dict[str, Any]:
        """
        Apply a successful payment.

        This now works through payment allocations rather than assuming
        one successful external intent alone fully settles the payable.
        """
        if not PaymentApplicationGuardService.can_apply(payment_intent):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' is not eligible "
                f"for internal application."
            )

        if payment_intent.payable is None:
            raise PaymentError(
                f"Payment '{payment_intent.reference}' has no payable object."
            )

        settlement_result = (
            PaymentAllocationApplicationService.apply_successful_external_payment(
                payment_intent=payment_intent,
                total_amount=total_amount,
            )
        )

        if settlement_result["fully_settled"]:
            handler_result = cls._route_fully_settled_payable(
                payment_intent=payment_intent
            )
        else:
            handler_result = {
                "domain": "payments",
                "object_id": payment_intent.payable.pk,
                "action": "await_remaining_settlement",
            }

        return {
            "payment_intent_id": payment_intent.id,
            "reference": payment_intent.reference,
            "purpose": payment_intent.purpose,
            "applied": settlement_result["fully_settled"],
            "settlement_result": settlement_result,
            "handler_result": handler_result,
        }

    @classmethod
    def _route_fully_settled_payable(
        cls,
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Route fully settled payable to its domain handler.
        """
        if payment_intent.purpose == PaymentIntentPurpose.ORDER:
            return cls._handle_order_payment(payment_intent=payment_intent)

        if payment_intent.purpose == PaymentIntentPurpose.SPECIAL_ORDER:
            return cls._handle_special_order_payment(
                payment_intent=payment_intent
            )

        if payment_intent.purpose == PaymentIntentPurpose.WALLET_TOP_UP:
            return cls._handle_wallet_top_up(payment_intent=payment_intent)

        if payment_intent.purpose == PaymentIntentPurpose.CLASS_PURCHASE:
            return cls._handle_class_purchase(payment_intent=payment_intent)

        if payment_intent.purpose == PaymentIntentPurpose.BUNDLE_PURCHASE:
            return cls._handle_bundle_purchase(payment_intent=payment_intent)

        if payment_intent.purpose == PaymentIntentPurpose.TIP:
            return cls._handle_tip_payment(payment_intent=payment_intent)

        raise PaymentError(
            f"Unsupported payment purpose '{payment_intent.purpose}'."
        )

    @staticmethod
    def _handle_order_payment(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        order = payment_intent.payable

        # TODO:
        # 1. Post ledger journal for fully settled order
        # 2. Mark order paid using order domain service
        # 3. Trigger notifications

        return {
            "domain": "orders",
            "object_id": order.pk,
            "action": "mark_paid",
        }

    @staticmethod
    def _handle_special_order_payment(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        special_order = payment_intent.payable

        # TODO:
        # Mark special order paid

        return {
            "domain": "special_orders",
            "object_id": special_order.pk,
            "action": "mark_paid",
        }

    @staticmethod
    def _handle_wallet_top_up(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        # TODO:
        # 1. Post ledger journal
        # 2. Credit wallet

        return {
            "domain": "wallets",
            "object_id": payment_intent.client_id,
            "action": "credit_wallet",
        }

    @staticmethod
    def _handle_class_purchase(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        class_purchase = payment_intent.payable

        # TODO:
        # Mark class purchase paid and grant access

        return {
            "domain": "classes",
            "object_id": class_purchase.pk,
            "action": "grant_access",
        }

    @staticmethod
    def _handle_bundle_purchase(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        bundle_purchase = payment_intent.payable

        # TODO:
        # Mark bundle purchase paid and grant access

        return {
            "domain": "classes",
            "object_id": bundle_purchase.pk,
            "action": "grant_bundle_access",
        }

    @staticmethod
    def _handle_tip_payment(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        tip = payment_intent.payable

        # TODO:
        # Mark tip paid and credit writer earnings if needed

        return {
            "domain": "tips",
            "object_id": tip.pk,
            "action": "mark_paid",
        }