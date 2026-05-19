"""
Compatibility logging helpers for legacy payment/refund callers.
"""

import logging

logger = logging.getLogger(__name__)


class AdminLog:
    @staticmethod
    def log_action(*, admin=None, action="", details="", **kwargs):
        logger.info(
            "Legacy admin payment log: %s",
            action,
            extra={"admin_id": getattr(admin, "id", None), "details": details},
        )


class PaymentLog:
    @staticmethod
    def log_event(payment, action="", details="", **kwargs):
        logger.info(
            "Legacy payment log: %s",
            action,
            extra={"payment_id": getattr(payment, "id", None), "details": details},
        )
