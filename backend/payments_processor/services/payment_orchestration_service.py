from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from payments_processor.services.payment_provider_service import (
    PaymentProviderService,
)
from wallets.models import WalletHold
from wallets.services.wallet_hold_service import WalletHoldService


class PaymentOrchestrationError(Exception):
    """Base orchestration error."""


class PaymentIntentStateError(PaymentOrchestrationError):
    """Invalid state transitions."""


class PaymentOrchestrationService:
    """
    Coordinates payment lifecycle:
    - provider init
    - verification/webhooks
    - wallet hold capture/release
    """

    # ------------------------------------------------------------------ #
    # SAFE ACCESSORS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_status(payment_intent: Any) -> str:
        return str(getattr(payment_intent, "status", "") or "").lower()

    @staticmethod
    def _get_reference(payment_intent: Any) -> str:
        reference = getattr(payment_intent, "reference", None)
        if reference:
            return str(reference)

        fallback = getattr(payment_intent, "pk", "")
        return f"payment-intent-{fallback}"

    @staticmethod
    def _get_wallet_hold(payment_intent: Any) -> WalletHold | None:
        hold = getattr(payment_intent, "wallet_hold", None)
        return cast(WalletHold | None, hold)

    @staticmethod
    def _set(instance: Any, field: str, value: Any) -> None:
        setattr(cast(Any, instance), field, value)

    @staticmethod
    def _save(instance: Any, fields: list[str]) -> None:
        cast(Any, instance).save(update_fields=fields)

    # ------------------------------------------------------------------ #
    # AUDIT
    # ------------------------------------------------------------------ #

    @staticmethod
    def _log_audit(
        *,
        action: str,
        payment_intent: Any,
        actor: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        try:
            AuditLogService.log_auto(
                action=action,
                actor=actor,
                target=payment_intent,
                metadata={
                    "payment_intent_id": getattr(
                        payment_intent, "pk", None
                    ),
                    "reference": PaymentOrchestrationService._get_reference(
                        payment_intent
                    ),
                    **(metadata or {}),
                },
            )
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # INITIALIZATION
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def initialize_payment(
        payment_intent: Any,
        *,
        triggered_by: Any | None = None,
    ) -> Any:
        checkout = PaymentProviderService.create_payment(payment_intent)

        PaymentOrchestrationService._set(
            payment_intent,
            "provider_reference",
            checkout.provider_reference,
        )

        if hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._set(
                payment_intent,
                "provider_response",
                checkout.raw_response,
            )

        if hasattr(payment_intent, "checkout_url"):
            PaymentOrchestrationService._set(
                payment_intent,
                "checkout_url",
                checkout.checkout_url or checkout.payment_url,
            )

        if hasattr(payment_intent, "client_secret"):
            PaymentOrchestrationService._set(
                payment_intent,
                "client_secret",
                checkout.client_secret,
            )

        if hasattr(payment_intent, "status"):
            if PaymentOrchestrationService._get_status(payment_intent) in {
                "",
                "draft",
                "created",
            }:
                PaymentOrchestrationService._set(
                    payment_intent,
                    "status",
                    "pending",
                )

        fields = ["provider_reference", "updated_at"]

        for f in ["provider_response", "checkout_url", "client_secret", "status"]:
            if hasattr(payment_intent, f):
                fields.append(f)

        PaymentOrchestrationService._save(payment_intent, fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.initialized",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "provider_reference": checkout.provider_reference,
            },
        )

        return payment_intent

    # ------------------------------------------------------------------ #
    # SUCCESS
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_payment_success(
        payment_intent: Any,
        *,
        provider_transaction_id: str = "",
        provider_response: dict[str, Any] | None = None,
        triggered_by: Any | None = None,
    ) -> Any:
        if PaymentOrchestrationService._get_status(payment_intent) == "success":
            return payment_intent

        hold = PaymentOrchestrationService._get_wallet_hold(payment_intent)

        if hold is not None:
            WalletHoldService.capture_hold(
                hold=hold,
            )

        PaymentOrchestrationService._set(
            payment_intent,
            "status",
            "success",
        )

        if provider_transaction_id and hasattr(
            payment_intent, "provider_transaction_id"
        ):
            PaymentOrchestrationService._set(
                payment_intent,
                "provider_transaction_id",
                provider_transaction_id,
            )

        if provider_response and hasattr(
            payment_intent, "provider_response"
        ):
            PaymentOrchestrationService._set(
                payment_intent,
                "provider_response",
                provider_response,
            )

        if hasattr(payment_intent, "paid_at"):
            PaymentOrchestrationService._set(
                payment_intent,
                "paid_at",
                timezone.now(),
            )

        fields = ["status", "updated_at"]

        if provider_transaction_id:
            fields.append("provider_transaction_id")

        if provider_response:
            fields.append("provider_response")

        if hasattr(payment_intent, "paid_at"):
            fields.append("paid_at")

        PaymentOrchestrationService._save(payment_intent, fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.succeeded",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "provider_transaction_id": provider_transaction_id,
                "wallet_hold_id": getattr(hold, "pk", None),
            },
        )

        return payment_intent

    # ------------------------------------------------------------------ #
    # FAILURE
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_payment_failed(
        payment_intent: Any,
        *,
        failure_reason: str = "",
        provider_response: dict[str, Any] | None = None,
        triggered_by: Any | None = None,
    ) -> Any:
        if PaymentOrchestrationService._get_status(payment_intent) == "failed":
            return payment_intent

        hold = PaymentOrchestrationService._get_wallet_hold(payment_intent)

        if hold is not None:
            if str(getattr(hold, "status", "")).lower() == "active":
                WalletHoldService.release_hold(
                    hold=hold,
                )

        PaymentOrchestrationService._set(
            payment_intent,
            "status",
            "failed",
        )

        if failure_reason and hasattr(payment_intent, "failure_reason"):
            PaymentOrchestrationService._set(
                payment_intent,
                "failure_reason",
                failure_reason,
            )

        if provider_response and hasattr(
            payment_intent, "provider_response"
        ):
            PaymentOrchestrationService._set(
                payment_intent,
                "provider_response",
                provider_response,
            )

        fields = ["status", "updated_at"]

        if failure_reason:
            fields.append("failure_reason")

        if provider_response:
            fields.append("provider_response")

        PaymentOrchestrationService._save(payment_intent, fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.failed",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "failure_reason": failure_reason,
                "wallet_hold_id": getattr(hold, "pk", None),
            },
        )

        return payment_intent