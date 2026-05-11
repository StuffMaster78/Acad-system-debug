from typing import TypedDict, Literal, Optional


class TipCreatedEvent(TypedDict):
    event_type: Literal["tip.created"]
    tip_id: int
    timestamp: str

    sender_id: int
    receiver_id: int
    amount_cents: int
    currency: str


class TipPaymentInitiatedEvent(TypedDict):
    event_type: Literal["tip.payment_initiated"]
    tip_id: int
    timestamp: str

    payment_intent_id: int
    provider_reference: str | None


class TipSucceededEvent(TypedDict):
    event_type: Literal["tip.succeeded"]
    tip_id: int
    timestamp: str

    payment_intent_id: int
    gross_amount_cents: int

    writer_share_cents: int
    platform_fee_cents: int

    wallet_used: bool


class TipFailedEvent(TypedDict):
    event_type: Literal["tip.failed"]
    tip_id: int
    timestamp: str

    reason: str
    payment_intent_id: int | None


class WalletHoldCreatedEvent(TypedDict):
    event_type: Literal["wallet.hold.created"]
    tip_id: int
    timestamp: str

    wallet_id: int
    hold_amount_cents: int