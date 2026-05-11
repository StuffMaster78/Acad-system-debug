from __future__ import annotations

from tips.enums.tip_status import TipStatus


class TipStateError(Exception):
    pass


class TipStateMachine:
    """
    Deterministic state machine for Tip lifecycle.

    RULE:
    - No invalid transitions allowed
    - Terminal states are final
    """

    ALLOWED_TRANSITIONS: dict[TipStatus, set[TipStatus]] = {
        TipStatus.PENDING: {
            TipStatus.PAYMENT_INITIATED,
            TipStatus.CANCELLED,
        },

        TipStatus.PAYMENT_INITIATED: {
            TipStatus.PROCESSING,
            TipStatus.FAILED,
            TipStatus.CANCELLED,
        },

        TipStatus.PROCESSING: {
            TipStatus.SUCCEEDED,
            TipStatus.FAILED,
            TipStatus.CANCELLED,
        },

        TipStatus.SUCCEEDED: set(),
        TipStatus.FAILED: set(),
        TipStatus.CANCELLED: set(),
    }

    # ---------------------------- #
    # CORE GUARD
    # ---------------------------- #

    @staticmethod
    def can_transition(from_status: TipStatus, to_status: TipStatus) -> bool:
        return to_status in TipStateMachine.ALLOWED_TRANSITIONS.get(from_status, set())

    # ---------------------------- #
    # STRICT TRANSITION
    # ---------------------------- #

    @staticmethod
    def transition(tip, new_status: TipStatus) -> None:
        current = tip.status

        if current == new_status:
            return

        if not TipStateMachine.can_transition(current, new_status):
            raise TipStateError(
                f"Invalid tip transition: {current} → {new_status}"
            )

        tip.status = new_status
        tip.save(update_fields=["status"])

    # ---------------------------- #
    # DOMAIN HELPERS (clean API)
    # ---------------------------- #

    @staticmethod
    def initiate_payment(tip) -> None:
        TipStateMachine.transition(
            tip,
            TipStatus.PAYMENT_INITIATED,
        )

    @staticmethod
    def process(tip) -> None:
        TipStateMachine.transition(
            tip,
            TipStatus.PROCESSING,
        )

    @staticmethod
    def succeed(tip) -> None:
        TipStateMachine.transition(
            tip,
            TipStatus.SUCCEEDED,
        )

    @staticmethod
    def fail(tip) -> None:
        TipStateMachine.transition(
            tip,
            TipStatus.FAILED,
        )

    @staticmethod
    def cancel(tip) -> None:
        TipStateMachine.transition(
            tip,
            TipStatus.CANCELLED,
        )