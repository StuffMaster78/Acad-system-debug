from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from payments_processor.services.payment_provider_service import PaymentProviderService
from wallets.models import WalletHold
from wallets.services import WalletHoldService


class PaymentOrchestrationError(Exception):
    """Base orchestration error."""


class PaymentIntentStateError(PaymentOrchestrationError):
    """Raised when a payment intent is in an invalid state."""


class PaymentOrchestrationService:
    """
    Coordinates payment intent lifecycle across:
    1. provider initialization
    2. provider verification/webhooks
    3. wallet hold capture/release for split payments
    4. transaction recording hooks

    Notes:
    - This service assumes payment_intent is a Django model instance.
    - It uses getattr/cast at the ORM boundary to stay sane with Pylance.
    - Replace inferred field names if your model differs.
    """

    @staticmethod
    def _get_status(payment_intent: Any) -> str:
        return str(getattr(payment_intent, "status", "") or "").lower()

    @staticmethod
    def _get_amount(payment_intent: Any) -> Decimal:
        return Decimal(str(getattr(payment_intent, "amount", "0.00")))

    @staticmethod
    def _get_currency(payment_intent: Any) -> str:
        return str(getattr(payment_intent, "currency", "USD"))

    @staticmethod
    def _get_reference(payment_intent: Any) -> str:
        reference = getattr(payment_intent, "reference", None)
        if reference:
            return str(reference)

        fallback = getattr(payment_intent, "id", "")
        return f"payment-intent-{fallback}"

    @staticmethod
    def _get_wallet_hold(payment_intent: Any) -> WalletHold | None:
        hold = getattr(payment_intent, "wallet_hold", None)
        return cast(WalletHold | None, hold)

    @staticmethod
    def _setattr(instance: Any, field_name: str, value: Any) -> None:
        setattr(cast(Any, instance), field_name, value)

    @staticmethod
    def _save(instance: Any, update_fields: list[str]) -> None:
        cast(Any, instance).save(update_fields=update_fields)

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
                # website=getattr(payment_intent, "website", None),
                metadata={
                    "payment_intent_id": cast(Any, payment_intent).id,
                    "reference": PaymentOrchestrationService._get_reference(
                        payment_intent
                    ),
                    **(metadata or {}),
                },
            )
        except Exception:
            pass

    @staticmethod
    @transaction.atomic
    def initialize_payment(payment_intent: Any, *, triggered_by: Any | None = None) -> Any:
        """
        Initialize provider-side payment and persist provider checkout details.
        """
        checkout_result = PaymentProviderService.create_payment(payment_intent)

        PaymentOrchestrationService._setattr(
            payment_intent,
            "provider_reference",
            checkout_result.provider_reference,
        )

        if hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_response",
                checkout_result.raw_response,
            )

        if hasattr(payment_intent, "checkout_url"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "checkout_url",
                checkout_result.checkout_url or checkout_result.payment_url,
            )

        if hasattr(payment_intent, "client_secret"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "client_secret",
                checkout_result.client_secret,
            )

        if hasattr(payment_intent, "status"):
            current_status = PaymentOrchestrationService._get_status(payment_intent)
            if current_status in {"", "draft", "created"}:
                PaymentOrchestrationService._setattr(
                    payment_intent,
                    "status",
                    "pending",
                )

        update_fields = ["provider_reference", "updated_at"]

        if hasattr(payment_intent, "provider_response"):
            update_fields.append("provider_response")

        if hasattr(payment_intent, "checkout_url"):
            update_fields.append("checkout_url")

        if hasattr(payment_intent, "client_secret"):
            update_fields.append("client_secret")

        if hasattr(payment_intent, "status"):
            update_fields.append("status")

        PaymentOrchestrationService._save(payment_intent, update_fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.initialized",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "provider_name": getattr(payment_intent, "provider_name", ""),
                "provider_reference": checkout_result.provider_reference,
            },
        )

        return payment_intent

    @staticmethod
    @transaction.atomic
    def mark_payment_success(
        payment_intent: Any,
        *,
        provider_transaction_id: str = "",
        provider_response: dict[str, Any] | None = None,
        triggered_by: Any | None = None,
    ) -> Any:
        """
        Mark payment as successful and capture wallet hold if present.
        """
        current_status = PaymentOrchestrationService._get_status(payment_intent)
        if current_status == "success":
            return payment_intent

        hold = PaymentOrchestrationService._get_wallet_hold(payment_intent)
        if hold is not None:
            WalletHoldService.capture_hold(
                hold=hold,
                captured_by=triggered_by,
            )

        PaymentOrchestrationService._setattr(payment_intent, "status", "success")

        if provider_transaction_id and hasattr(payment_intent, "provider_transaction_id"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_transaction_id",
                provider_transaction_id,
            )

        if provider_response is not None and hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_response",
                provider_response,
            )

        if hasattr(payment_intent, "paid_at"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "paid_at",
                timezone.now(),
            )

        update_fields = ["status", "updated_at"]

        if provider_transaction_id and hasattr(payment_intent, "provider_transaction_id"):
            update_fields.append("provider_transaction_id")

        if provider_response is not None and hasattr(payment_intent, "provider_response"):
            update_fields.append("provider_response")

        if hasattr(payment_intent, "paid_at"):
            update_fields.append("paid_at")

        PaymentOrchestrationService._save(payment_intent, update_fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.succeeded",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "provider_transaction_id": provider_transaction_id,
                "wallet_hold_id": cast(Any, hold).id if hold is not None else None,
            },
        )

        return payment_intent

    @staticmethod
    @transaction.atomic
    def mark_payment_failed(
        payment_intent: Any,
        *,
        failure_reason: str = "",
        provider_response: dict[str, Any] | None = None,
        triggered_by: Any | None = None,
    ) -> Any:
        """
        Mark payment as failed and release wallet hold if present.
        """
        current_status = PaymentOrchestrationService._get_status(payment_intent)
        if current_status == "failed":
            return payment_intent

        hold = PaymentOrchestrationService._get_wallet_hold(payment_intent)
        if hold is not None:
            hold_status = str(getattr(hold, "status", "")).lower()
            if hold_status == "active":
                WalletHoldService.release_hold(
                    hold=hold,
                    released_by=triggered_by,
                )

        PaymentOrchestrationService._setattr(payment_intent, "status", "failed")

        if failure_reason and hasattr(payment_intent, "failure_reason"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "failure_reason",
                failure_reason,
            )

        if provider_response is not None and hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_response",
                provider_response,
            )

        update_fields = ["status", "updated_at"]

        if failure_reason and hasattr(payment_intent, "failure_reason"):
            update_fields.append("failure_reason")

        if provider_response is not None and hasattr(payment_intent, "provider_response"):
            update_fields.append("provider_response")

        PaymentOrchestrationService._save(payment_intent, update_fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.failed",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "failure_reason": failure_reason,
                "wallet_hold_id": cast(Any, hold).id if hold is not None else None,
            },
        )

        return payment_intent

    @staticmethod
    @transaction.atomic
    def refresh_from_provider(
        payment_intent: Any,
        *,
        triggered_by: Any | None = None,
    ) -> Any:
        """
        Pull latest status from provider and apply outcome.
        """
        verification = PaymentProviderService.verify_payment(payment_intent)

        if verification.status == "success":
            return PaymentOrchestrationService.mark_payment_success(
                payment_intent,
                provider_transaction_id=verification.provider_transaction_id,
                provider_response=verification.raw_response,
                triggered_by=triggered_by,
            )

        if verification.status == "failed":
            return PaymentOrchestrationService.mark_payment_failed(
                payment_intent,
                failure_reason="Provider verification marked payment as failed.",
                provider_response=verification.raw_response,
                triggered_by=triggered_by,
            )

        if hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_response",
                verification.raw_response,
            )
            PaymentOrchestrationService._save(
                payment_intent,
                ["provider_response", "updated_at"],
            )

        PaymentOrchestrationService._log_audit(
            action="payment.intent.refreshed",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "verification_status": verification.status,
                "provider_transaction_id": verification.provider_transaction_id,
            },
        )

        return payment_intent

    @staticmethod
    @transaction.atomic
    def process_webhook(
        *,
        provider_name: str,
        payload: dict[str, Any],
        headers: dict[str, Any],
        payment_intent: Any,
        triggered_by: Any | None = None,
    ) -> Any:
        """
        Verify provider webhook, parse normalized event, and apply state transition.
        """
        verification = PaymentProviderService.verify_webhook(
            provider_name=provider_name,
            payload=payload,
            headers=headers,
        )

        if not verification.is_valid:
            raise PaymentOrchestrationError(
                verification.error_message or "Invalid webhook."
            )

        event = PaymentProviderService.parse_webhook(
            provider_name=provider_name,
            payload=payload,
        )

        if event.status == "success":
            return PaymentOrchestrationService.mark_payment_success(
                payment_intent,
                provider_transaction_id=event.provider_transaction_id,
                provider_response=event.raw_payload,
                triggered_by=triggered_by,
            )

        if event.status == "failed":
            return PaymentOrchestrationService.mark_payment_failed(
                payment_intent,
                failure_reason=f"Webhook event {event.event_type} marked payment failed.",
                provider_response=event.raw_payload,
                triggered_by=triggered_by,
            )

        if hasattr(payment_intent, "provider_response"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "provider_response",
                event.raw_payload,
            )
            PaymentOrchestrationService._save(
                payment_intent,
                ["provider_response", "updated_at"],
            )

        PaymentOrchestrationService._log_audit(
            action="payment.intent.webhook_processed",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "event_id": event.event_id,
                "event_type": event.event_type,
                "event_status": event.status,
                "provider_transaction_id": event.provider_transaction_id,
            },
        )

        return payment_intent

    @staticmethod
    @transaction.atomic
    def create_wallet_backed_intent(
        *,
        payment_intent: Any,
        total_amount: Decimal,
        wallet_split_result: dict[str, Any],
        triggered_by: Any | None = None,
    ) -> Any:
        """
        Persist split payment values on the intent if your model supports them.
        """
        wallet_amount = Decimal(str(wallet_split_result.get("wallet_amount", "0.00")))
        gateway_amount = Decimal(str(wallet_split_result.get("gateway_amount", "0.00")))
        wallet_hold = wallet_split_result.get("wallet_hold")

        if hasattr(payment_intent, "amount"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "amount",
                total_amount,
            )

        if hasattr(payment_intent, "wallet_amount"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "wallet_amount",
                wallet_amount,
            )

        if hasattr(payment_intent, "gateway_amount"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "gateway_amount",
                gateway_amount,
            )

        if wallet_hold is not None and hasattr(payment_intent, "wallet_hold"):
            PaymentOrchestrationService._setattr(
                payment_intent,
                "wallet_hold",
                wallet_hold,
            )

        if hasattr(payment_intent, "status"):
            current_status = PaymentOrchestrationService._get_status(payment_intent)
            if current_status in {"", "draft", "created"}:
                PaymentOrchestrationService._setattr(
                    payment_intent,
                    "status",
                    "pending",
                )

        update_fields = ["updated_at"]

        for candidate in [
            "amount",
            "wallet_amount",
            "gateway_amount",
            "wallet_hold",
            "status",
        ]:
            if hasattr(payment_intent, candidate):
                update_fields.append(candidate)

        PaymentOrchestrationService._save(payment_intent, update_fields)

        PaymentOrchestrationService._log_audit(
            action="payment.intent.wallet_split_attached",
            payment_intent=payment_intent,
            actor=triggered_by,
            metadata={
                "total_amount": str(total_amount),
                "wallet_amount": str(wallet_amount),
                "gateway_amount": str(gateway_amount),
                "wallet_hold_id": cast(Any, wallet_hold).id
                if wallet_hold is not None
                else None,
            },
        )

        return payment_intent