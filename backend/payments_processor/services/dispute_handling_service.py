from payments_processor.enums import PaymentIntentStatus
from payments_processor.exceptions import PaymentError


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    PaymentIntentStatus.CREATED: {
        PaymentIntentStatus.PENDING,
        PaymentIntentStatus.CANCELED,
        PaymentIntentStatus.EXPIRED,
    },
    PaymentIntentStatus.PENDING: {
        PaymentIntentStatus.PROCESSING,
        PaymentIntentStatus.REQUIRES_ACTION,
        PaymentIntentStatus.SUCCEEDED,
        PaymentIntentStatus.FAILED,
        PaymentIntentStatus.CANCELED,
        PaymentIntentStatus.EXPIRED,
    },
    PaymentIntentStatus.PROCESSING: {
        PaymentIntentStatus.SUCCEEDED,
        PaymentIntentStatus.FAILED,
    },
    PaymentIntentStatus.REQUIRES_ACTION: {
        PaymentIntentStatus.PROCESSING,
        PaymentIntentStatus.CANCELED,
    },
    PaymentIntentStatus.SUCCEEDED: {
        PaymentIntentStatus.PARTIALLY_REFUNDED,
        PaymentIntentStatus.REFUNDED,
    },
    PaymentIntentStatus.PARTIALLY_REFUNDED: {
        PaymentIntentStatus.REFUNDED,
    },
    PaymentIntentStatus.FAILED: set(),
    PaymentIntentStatus.CANCELED: set(),
    PaymentIntentStatus.EXPIRED: set(),
    PaymentIntentStatus.REFUNDED: set(),
}


def validate_webhook_status_transition(
    *,
    current_status: str,
    new_status: str,
) -> None:
    """
    Validate allowed payment intent status transitions.

    This prevents:
    - regressive transitions (e.g. succeeded → pending)
    - invalid overrides (e.g. refunded → anything)
    - inconsistent provider behavior

    Args:
        current_status: Existing payment status.
        new_status: Incoming status from webhook.

    Raises:
        PaymentError: If transition is invalid.
    """
    if current_status == new_status:
        return

    allowed = _ALLOWED_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise PaymentError(
            f"Invalid status transition '{current_status}' → "
            f"'{new_status}'."
        )