from datetime import datetime, timezone

from tips.contracts.tip_event_contracts import (
    TipCreatedEvent,
    TipSucceededEvent,
    TipFailedEvent,
)


class TipEventFactory:

    @staticmethod
    def created(
        *,
        tip
    ) -> TipCreatedEvent:
        return {
            "event_type": "tip.created",
            "tip_id": tip.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender_id": tip.sender_id,
            "receiver_id": tip.receiver_id,
            "amount_cents": int(tip.gross_amount),
            "currency": tip.currency,
        }

    @staticmethod
    def succeeded(
        *,
        tip,
        payment_intent,
        writer_share,
        platform_fee
    ) -> TipSucceededEvent:
        return {
            "event_type": "tip.succeeded",
            "tip_id": tip.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payment_intent_id": payment_intent.id,
            "gross_amount_cents": int(tip.gross_amount),
            "writer_share_cents": int(writer_share),
            "platform_fee_cents": int(platform_fee),
            "wallet_used": payment_intent.wallet_hold_id is not None,
        }

    @staticmethod
    def failed(
        *,
        tip,
        reason,
        payment_intent=None
    ) -> TipFailedEvent:
        return {
            "event_type": "tip.failed",
            "tip_id": tip.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "payment_intent_id": getattr(payment_intent, "id", None),
        }