from __future__ import annotations

from rest_framework.throttling import UserRateThrottle


class CommunicationMessageSendThrottle(UserRateThrottle):
    """
    Throttle message creation.

    Prevents clients, writers, or staff from spamming threads.
    """

    scope = "communication_message_send"


class CommunicationThreadCreateThrottle(UserRateThrottle):
    """
    Throttle thread creation.
    """

    scope = "communication_thread_create"


class CommunicationModerationActionThrottle(UserRateThrottle):
    """
    Throttle moderation actions such as hide, withdraw, approve, reject,
    block, and resolve.
    """

    scope = "communication_moderation_action"


class CommunicationScreeningRuleWriteThrottle(UserRateThrottle):
    """
    Throttle screening rule writes.

    Admin mistakes here can affect platform safety, so keep writes deliberate.
    """

    scope = "communication_screening_rule_write"


class CommunicationSSEThrottle(UserRateThrottle):
    """
    Throttle SSE connection attempts.
    """

    scope = "communication_sse_connect"


class CommunicationReadReceiptThrottle(UserRateThrottle):
    """
    Throttle read receipt writes.
    """

    scope = "communication_read_receipt"