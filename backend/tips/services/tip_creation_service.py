from __future__ import annotations

from django.db import transaction

from tips.contracts.tip_creation_contract import TipCreationContract
from tips.models.tip import Tip

from tips.services.tip_policy_resolver import TipPolicyResolver
from tips.services.tip_validation_service import TipValidationService
from tips.services.tip_attribution_service import TipAttributionService
from tips.services.tip_idempotency_service import TipIdempotencyService
from tips.services.tip_payment_router_service import TipPaymentRouterService

from audit_logging.services.audit_service import AuditService
from notifications_system.services.notification_service import NotificationService

from tips.services.tip_wcs_bridge import TipWCSBridge

class TipCreationService:
    """
    Thin orchestration entry point for tip creation.
    """

    @classmethod
    @transaction.atomic
    def create(cls, contract: TipCreationContract) -> Tip:

        idempotency_obj, _ = TipIdempotencyService.get_or_create_key(
            sender=contract.sender,
            key=contract.idempotency_key,
            payload=contract.payload(),
        )

        policy = TipPolicyResolver.get_active_policy()

        TipValidationService.validate(
            policy=policy,
            amount=contract.gross_amount,
        )

        TipAttributionService.validate(
            context_type=contract.context_type,
            order_id=contract.order_id,
            special_order_id=contract.special_order_id,
            class_purchase_id=contract.class_purchase_id,
            reason=contract.reason,
        )

        tip = Tip.objects.create(
            sender=contract.sender,
            receiver=contract.receiver,
            gross_amount=contract.gross_amount,
            currency=contract.currency,
            source_type=contract.source_type,
            status="pending",
            active_policy=policy,
            client_note=contract.reason,
            idempotency_key=idempotency_obj,
        )

        TipAttributionService.create_attribution(
            tip=tip,
            context_type=contract.context_type,
            order_id=contract.order_id,
            special_order_id=contract.special_order_id,
            class_purchase_id=contract.class_purchase_id,
            reason=contract.reason,
        )

        routing = TipPaymentRouterService.route(tip=tip, contract=contract)

        tip.payment_intent = routing.get("payment_intent")
        tip.save(update_fields=["payment_intent"])

        # Fire WCS bridge — tip is now confirmed.
        # fire WCS bridge after payment routing.
        # Previously TipWCSBridge was imported but never called —
        # the tip was never entered into the writer compensation system.
        #
        # fire_safe() updates tip.status, tip.settlement_reference,
        # and tip.paid_at in place. We save those fields immediately.
        #
        # On failure (no open window) tip.status = FAILED.
        # Admin retries via POST /admin/tips/{pk}/retry/
        # The retry is idempotent — same idempotency key returns the
        # existing CompensationEvent on a second attempt.
        TipWCSBridge.fire_safe(tip)
        tip.save(
            update_fields=[
                "status",
                "compensation_event",
                "confirmed_at",
            ],
        )


        AuditService.record(
            action="tip.created",
            actor=contract.sender,
            obj=tip,
            website=getattr(contract.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "mode": routing.get("mode"),
            },
        )

        NotificationService.notify(
            website=getattr(contract.sender, "website", None),
            event_key="tips.initiated",
            recipient=contract.receiver,
            context={
                "tip_id": tip.pk,
                "amount": str(contract.gross_amount),
                "mode": routing.get("mode"),
            },
            channels=["email", "in_app"],
            is_critical=True,
        )

        TipIdempotencyService.bind_tip(
            idempotency_obj=idempotency_obj,
            tip=tip,
        )

        return tip