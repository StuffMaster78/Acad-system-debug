from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction

from wallets.services.wallet_hold_service import WalletHoldService
from payments_processor.models.payment_intent import PaymentIntent
from payments_processor.enums import PaymentIntentPurpose
from payments_processor.services.payment_provider_service import PaymentProviderService

from payments_processor.services.payment_orchestration_service import (
    PaymentOrchestrationService,
)


class TipPaymentRoutingError(Exception):
    pass


class TipPaymentRouterService:
    """
    Single decision authority for tip payments.

    RULE:
    - This is the ONLY place that decides wallet vs checkout.
    - No other service should branch payment logic.
    """

    # ------------------------------------------------------------ #
    # PUBLIC ENTRY
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def route(*, tip, contract) -> dict[str, Any]:
        """
        Returns a routing result containing:
        - payment_intent (optional)
        - wallet_hold (optional)
        - mode (wallet | checkout | hybrid)
        """

        wallet = getattr(contract.sender, "wallet", None)
        amount: Decimal = contract.gross_amount

        wallet_hold = None
        payment_intent = None

        wallet_balance = getattr(wallet, "available_balance", Decimal("0"))

        # -------------------------------------------------------- #
        # 1. FULL WALLET COVER
        # -------------------------------------------------------- #
        if wallet and wallet_balance >= amount:
            wallet_hold = WalletHoldService.create_hold(
                wallet=wallet,
                amount=amount,
                website=getattr(contract.sender, "website", None),
                reason="TIP_FULL_WALLET",
                created_by=contract.sender,
                reference=f"tip:{tip.pk}",
                reference_type="tip",
                reference_id=str(tip.pk),
            )

            # immediate capture = instant success path
            WalletHoldService.capture_hold(
                hold=wallet_hold,
                captured_by=contract.sender,
            )

            return {
                "mode": "wallet",
                "wallet_hold": wallet_hold,
                "payment_intent": None,
            }

        # -------------------------------------------------------- #
        # 2. PARTIAL WALLET (HYBRID)
        # -------------------------------------------------------- #
        if wallet and wallet_balance > Decimal("0"):
            wallet_hold = WalletHoldService.create_hold(
                wallet=wallet,
                amount=wallet_balance,
                website=getattr(contract.sender, "website", None),
                reason="TIP_PARTIAL_WALLET",
                created_by=contract.sender,
                reference=f"tip:{tip.pk}",
                reference_type="tip",
                reference_id=str(tip.pk),
            )

            remaining = amount - wallet_balance
        else:
            remaining = amount

        # -------------------------------------------------------- #
        # 3. EXTERNAL CHECKOUT FLOW
        # -------------------------------------------------------- #
        payment_intent = PaymentIntent.objects.create(
            website=getattr(contract.sender, "website", None),
            client=contract.sender,
            amount=remaining,
            purpose=PaymentIntentPurpose.TIP,
            currency=contract.currency,
            payable=tip,
            wallet_hold=wallet_hold,
            status="created",
        )

        checkout = PaymentProviderService.create_payment(payment_intent)

        payment_intent.provider_intent_id = getattr(
            checkout, "provider_intent_id", ""
        )
        payment_intent.provider_checkout_url = getattr(
            checkout, "checkout_url", ""
        )
        payment_intent.provider_client_secret = getattr(
            checkout, "client_secret", ""
        )
        payment_intent.provider_response = getattr(
            checkout, "raw_response", {}
        )

        payment_intent.save(
            update_fields=[
                "provider_intent_id",
                "provider_checkout_url",
                "provider_client_secret",
                "provider_response",
            ]
        )

        # finalize provider orchestration state
        PaymentOrchestrationService.initialize_payment(
            payment_intent,
            triggered_by=contract.sender,
        )

        return {
            "mode": "checkout",
            "wallet_hold": wallet_hold,
            "payment_intent": payment_intent,
        }