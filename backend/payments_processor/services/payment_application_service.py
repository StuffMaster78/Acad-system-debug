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

from billing.models.payment_request import PaymentRequest

class PaymentApplicationService:
    """
    Applies successful payments internally in a safe, idempotent,
    and settlement-aware manner.

    Responsibilities:
    - Validate application eligibility
    - Apply allocations (wallet + external)
    - Route fully settled payables
    - Ensure idempotency and failure tracking
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

        Args:
            payment_intent: PaymentIntent instance
            total_amount: Expected total settlement amount

        Returns:
            Structured result describing settlement outcome

        Raises:
            PaymentError: If application fails or is invalid
        """
        cls._validate_application_inputs(
            payment_intent=payment_intent,
            total_amount=total_amount,
        )

        # cls._increment_application_attempt(payment_intent)

        try:
            settlement_result = (
                PaymentAllocationApplicationService
                .apply_successful_external_payment(
                    payment_intent=payment_intent,
                    total_amount=total_amount,
                )
            )

            fully_settled = bool(
                settlement_result.get("fully_settled", False)
            )

            if fully_settled:
                handler_result = cls._route_fully_settled_payable(
                    payment_intent=payment_intent,
                )

                PaymentApplicationGuardService.mark_as_applied(
                    payment_intent
                )
            else:
                handler_result = {
                    "domain": "payments",
                    "object_id": (
                        payment_intent.payable_object_id
                        if payment_intent.payable_object_id
                        else None
                    ),
                    "action": "await_remaining_settlement",
                }

            return {
                "payment_intent_id": payment_intent.pk,
                "reference": payment_intent.reference,
                "purpose": payment_intent.purpose,
                "applied": fully_settled,
                "settlement_result": settlement_result,
                "handler_result": handler_result,
            }

        except Exception as exc:
            PaymentApplicationGuardService.mark_as_failed(
                payment_intent=payment_intent,
                error=str(exc),
            )
            raise

    # ------------------------------------------------------------------ #
    # INTERNAL HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_application_inputs(
        *,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> None:
        """
        Validate application preconditions.

        Raises:
            PaymentError
        """
        if not PaymentApplicationGuardService.can_apply(payment_intent):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' is not "
                f"eligible for application."
            )

        if (
            payment_intent.purpose != PaymentIntentPurpose.WALLET_TOP_UP
            and payment_intent.payable is None
        ):
            raise PaymentError(
                f"Payment '{payment_intent.reference}' has no payable."
            )

        if total_amount <= Decimal("0.00"):
            raise PaymentError("Total amount must be greater than zero.")

    @staticmethod
    def _increment_application_attempt(
        payment_intent: PaymentIntent,
    ) -> None:
        """
        Increment application attempt counter.
        """
        payment_intent.application_attempts += 1
        payment_intent.save(update_fields=["application_attempts"])

    # ------------------------------------------------------------------ #
    # ROUTING
    # ------------------------------------------------------------------ #

    @classmethod
    def _route_fully_settled_payable(
        cls,
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Route payable to correct domain handler.
        """
        purpose = payment_intent.purpose

        if purpose == PaymentIntentPurpose.ORDER:
            return cls._handle_order_payment(payment_intent)

        if purpose == PaymentIntentPurpose.SPECIAL_ORDER:
            return cls._handle_special_order_payment(payment_intent)

        if purpose == PaymentIntentPurpose.WALLET_TOP_UP:
            return cls._handle_wallet_top_up(payment_intent)

        if purpose == PaymentIntentPurpose.CLASS_PURCHASE:
            return cls._handle_class_purchase(payment_intent)

        if purpose == PaymentIntentPurpose.BUNDLE_PURCHASE:
            return cls._handle_bundle_purchase(payment_intent)

        if purpose == PaymentIntentPurpose.TIP:
            return cls._handle_tip_payment(payment_intent)
        
        if purpose == PaymentIntentPurpose.INVOICE:
            return cls._handle_invoice_payment(payment_intent=payment_intent)

        if purpose == PaymentIntentPurpose.BILLING_PAYMENT_REQUEST:
            return cls._handle_billing_payment_request(
                payment_intent=payment_intent
            )

        raise PaymentError(
            f"Unsupported payment purpose '{purpose}'."
        )

    # ------------------------------------------------------------------ #
    # DOMAIN HANDLERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _handle_order_payment(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle order settlement.
        """
        order = payment_intent.payable

        if order is None:
            raise PaymentError("Order payable missing.")

        # TODO: integrate OrderService.mark_paid(order)

        return {
            "domain": "orders",
            "object_id": getattr(order, "pk", None),
            "action": "mark_paid",
        }

    @staticmethod
    def _handle_special_order_payment(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle special order settlement.
        """
        special_order = payment_intent.payable

        if special_order is None:
            raise PaymentError("Special order payable missing.")

        return {
            "domain": "special_orders",
            "object_id": getattr(special_order, "pk", None),
            "action": "mark_paid",
        }

    @staticmethod
    def _handle_wallet_top_up(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle wallet top-up settlement.
        """
        # NOTE:
        # This should eventually call:
        # WalletService.credit_wallet(...)
        # ClientWalletService.fund_wallet(
        #     website=website,
        #     client=client,
        #     amounyt=wamount,
        #     created_by=user,
        #     description=description,
        #     reference_type=reference_type,
        #     metadata={},

        # )

        return {
            "domain": "wallets",
            "object_id": payment_intent.client.pk,
            "action": "credit_wallet",
        }

    @staticmethod
    def _handle_class_purchase(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle class purchase settlement.
        """
        class_purchase = payment_intent.payable

        if class_purchase is None:
            raise PaymentError("Class purchase payable missing.")

        return {
            "domain": "classes",
            "object_id": getattr(class_purchase, "pk", None),
            "action": "grant_access",
        }

    @staticmethod
    def _handle_bundle_purchase(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle bundle purchase settlement.
        """
        bundle = payment_intent.payable

        if bundle is None:
            raise PaymentError("Bundle payable missing.")

        return {
            "domain": "classes",
            "object_id": getattr(bundle, "pk", None),
            "action": "grant_bundle_access",
        }

    @staticmethod
    def _handle_tip_payment(
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Handle tip settlement.
        """
        tip = payment_intent.payable

        if tip is None:
            raise PaymentError("Tip payable missing.")

        return {
            "domain": "tips",
            "object_id": getattr(tip, "pk", None),
            "action": "mark_paid",
        }
    

    @staticmethod
    def _handle_invoice_payment(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Route a fully settled invoice payable back to the billing domain.

        Args:
            payment_intent:
                Fully settled payment intent whose payable object is a
                billing invoice.

        Returns:
            dict[str, Any]:
                Structured routing result describing the billing action.

        Raises:
            PaymentError:
                Raised when the payable object is missing or has the wrong
                type.
        """
        from billing.models.invoice import Invoice

        payable = payment_intent.payable

        if payable is None:
            raise PaymentError(
                "Invoice settlement requires a payable object."
            )

        if not isinstance(payable, Invoice):
            raise PaymentError(
                "Invoice settlement received an invalid payable object."
            )

        return {
            "domain": "billing",
            "object_id": payable.pk,
            "action": "mark_paid",
        }
    

    @staticmethod
    def _handle_billing_payment_request(
        *,
        payment_intent: PaymentIntent,
    ) -> dict[str, Any]:
        """
        Route a fully settled billing payment request back to the billing
        domain.

        Args:
            payment_intent:
                Fully settled payment intent whose payable object is a
                billing payment request.

        Returns:
            dict[str, Any]:
                Structured routing result describing the billing action.

        Raises:
            PaymentError:
                Raised when the payable object is missing or has the wrong
                type.
        """
        payable = payment_intent.payable

        if payable is None:
            raise PaymentError(
                "Billing payment request settlement requires a payable "
                "object."
            )

        if not isinstance(payable, PaymentRequest):
            raise PaymentError(
                "Billing payment request settlement received an invalid "
                "payable object."
            )

        return {
            "domain": "billing",
            "object_id": payable.pk,
            "action": "mark_paid",
        }