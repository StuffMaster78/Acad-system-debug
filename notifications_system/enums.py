# notifications_system/enums.py
from __future__ import annotations

from enum import IntEnum
from typing import Iterable, List, Set, Tuple

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


# =========================
# Channels / Delivery Types
# =========================

class NotificationChannel(TextChoices):
    EMAIL = "email", _("Email")
    IN_APP = "in_app", _("In-app")
    SMS = "sms", _("SMS")
    WS = "ws", _("WebSocket")
    SSE = "sse", _("Server-Sent Events")
    PUSH = "push", _("Push")
    WEBHOOK = "webhook", _("Webhook")
    TELEGRAM = "telegram", _("Telegram")
    DISCORD = "discord", _("Discord")
    SYSTEM = "system", _("System")

# Alias to keep legacy imports working
NotificationType = NotificationChannel


# ===============
# Status & Labels
# ===============

class DeliveryStatus(TextChoices):
    PENDING = "pending", _("Pending")
    QUEUED = "queued", _("Queued")
    SENT = "sent", _("Sent")
    RETRY = "retry", _("Retry")
    DELAYED = "delayed", _("Delayed")
    TIMEOUT = "timeout", _("Timeout")
    FAILED = "failed", _("Failed")


class NotificationCategory(TextChoices):
    INFO = "info", _("Info")
    WARNING = "warning", _("Warning")
    ERROR = "error", _("Error")
    ANNOUNCEMENT = "announcement", _("Announcement")
    NEWS = "news", _("News")


class DigestType(TextChoices):
    DAILY = "daily_summary", _("Daily Summary")
    WEEKLY = "weekly_summary", _("Weekly Summary")
    CRITICAL = "critical_alerts", _("Critical Alerts")


# ===================
# Priority (IntEnum)
# ===================

class NotificationPriority(IntEnum):
    EMERGENCY = 1
    HIGH = 2
    MEDIUM_HIGH = 3
    NORMAL = 5
    LOW = 7
    PASSIVE = 10

    @classmethod
    def choices(cls) -> List[Tuple[int, str]]:
        return [(m.value, m.name.replace("_", " ").title()) for m in cls]


# ================
# Grouped Event Enums
# ================

class OrderEvent(TextChoices):
    ASSIGNED = "order_assigned", _("Order Assigned")
    ON_HOLD = "order_on_hold", _("Order On Hold")
    COMPLETED = "order_completed", _("Order Completed")
    CANCELLED = "order_cancelled", _("Order Cancelled")
    REJECTED = "order_rejected", _("Order Rejected")
    UPDATED = "order_updated", _("Order Updated")
    CREATED = "order_created", _("Order Created")
    APPROVED = "order_approved", _("Order Approved")
    ARCHIVED = "order_archived", _("Order Archived")
    RESTORED = "order_restored", _("Order Restored")
    REOPENED = "order_reopened", _("Order Reopened")
    REASSIGNED = "order_reassigned", _("Order Reassigned")
    RATED = "order_rated", _("Order Rated")
    REVIEWED = "order_reviewed", _("Order Reviewed")
    PAYMENT_FAILED = "order_payment_failed", _("Order Payment Failed")
    PAYMENT_SUCCESS = "order_payment_success", _("Order Payment Success")
    REFUNDED = "order_refunded", _("Order Refunded")
    ON_DISPUTE = "order_on_dispute", _("Order On Dispute")
    DISPUTE_RESOLVED = "order_dispute_resolved", _("Order Dispute Resolved")
    DISPUTE_ESCALATED = "order_dispute_escalated", _("Order Dispute Escalated")
    DISPUTE_CLOSED = "order_dispute_closed", _("Order Dispute Closed")
    REVIEW_REQUESTED = "order_review_requested", _("Order Review Requested")
    REVIEW_SUBMITTED = "order_review_submitted", _("Order Review Submitted")
    REVIEW_APPROVED = "order_review_approved", _("Order Review Approved")
    REVIEW_REJECTED = "order_review_rejected", _("Order Review Rejected")


class FileEvent(TextChoices):
    UPLOADED = "file_uploaded", _("File Uploaded")
    DELETED = "file_deleted", _("File Deleted")
    UPDATED = "file_updated", _("File Updated")


class WalletEvent(TextChoices):
    BALANCE_LOW = "wallet_balance_low", _("Wallet Balance Low")
    CREDITED = "wallet_credited", _("Wallet Credited")
    DEBITED = "wallet_debited", _("Wallet Debited")
    TX_FAILED = "wallet_transaction_failed", _("Wallet Transaction Failed")
    TX_SUCCESS = "wallet_transaction_success", _("Wallet Transaction Success")
    REFUND_INITIATED = "wallet_refund_initiated", _("Wallet Refund Initiated")
    REFUND_COMPLETED = "wallet_refund_completed", _("Wallet Refund Completed")


class PayoutEvent(TextChoices):
    PROCESSING = "payout_processing", _("Payout Processing")
    COMPLETED = "payout_completed", _("Payout Completed")
    FAILED = "payout_failed", _("Payout Failed")
    CANCELLED = "payout_cancelled", _("Payout Cancelled")


class TicketEvent(TextChoices):
    CREATED = "ticket_created", _("Ticket Created")
    UPDATED = "ticket_updated", _("Ticket Updated")
    CLOSED = "ticket_closed", _("Ticket Closed")
    REOPENED = "ticket_reopened", _("Ticket Reopened")
    ASSIGNED = "ticket_assigned", _("Ticket Assigned")
    UNASSIGNED = "ticket_unassigned", _("Ticket Unassigned")
    ESCALATED = "ticket_escalated", _("Ticket Escalated")
    RESOLVED = "ticket_resolved", _("Ticket Resolved")
    COMMENT_ADDED = "ticket_comment_added", _("Ticket Comment Added")
    COMMENT_UPDATED = "ticket_comment_updated", _("Ticket Comment Updated")
    COMMENT_DELETED = "ticket_comment_deleted", _("Ticket Comment Deleted")


class AccountEvent(TextChoices):
    PASSWORD_RESET = "password_reset", _("Password Reset")
    ACCOUNT_SUSPENDED = "account_suspended", _("Account Suspended")
    USER_VERIFIED = "user_verified", _("User Verified")
    USER_UNVERIFIED = "user_unverified", _("User Unverified")
    USER_BLACKLISTED = "user_blacklisted", _("User Blacklisted")
    USER_UNBLACKLISTED = "user_unblacklisted", _("User Unblacklisted")


class MessageEvent(TextChoices):
    NEW_MESSAGE = "new_message", _("New Message")


class WriterEvent(TextChoices):
    REVIEWED = "writer_reviewed", _("Writer Reviewed")
    SUSPENDED = "writer_suspended", _("Writer Suspended")
    PROBATION = "writer_sent_on_probation", _("Writer Sent on Probation")
    STRIKED = "writer_striked", _("Writer Striked")
    UNSTRIKED = "writer_unstriked", _("Writer Unstriked")
    WARNING = "writer_warning", _("Writer Warning")
    BANNED = "writer_banned", _("Writer Banned")
    UNBANNED = "writer_unbanned", _("Writer Unbanned")
    REINSTATED = "writer_reinstated", _("Writer Reinstated")
    REJECTED = "writer_rejected", _("Writer Rejected")
    APPROVED = "writer_approved", _("Writer Approved")
    ON_HOLD = "writer_on_hold", _("Writer On Hold")
    ON_PROBATION = "writer_on_probation", _("Writer On Probation")
    PROMOTED = "writer_promoted", _("Writer Promoted")
    DEMOTED = "writer_demoted", _("Writer Demoted")
    REVIEW_REQUESTED = "writer_review_requested", _("Writer Review Requested")
    REVIEW_SUBMITTED = "writer_review_submitted", _("Writer Review Submitted")
    REVIEW_APPROVED = "writer_review_approved", _("Writer Review Approved")

# =======
# Groups (back-compat for legacy imports expecting EventType)
# =======
class EventType(TextChoices):
    ORDERS   = "orders",   _("Orders")
    PAYMENTS = "payments", _("Payments")
    WRITERS  = "writers",  _("Writers")
    CLIENTS  = "clients",  _("Clients")
    SECURITY = "security", _("Security")
    SYSTEM   = "system",   _("System")
    CUSTOM   = "custom",   _("Custom")

# ==========================
# Helpers for grouped events
# ==========================

def all_event_values() -> Set[str]:
    """
    Flatten and return a set of all event values across grouped enums.
    """
    groups: Iterable[TextChoices] = (
        OrderEvent, FileEvent, WalletEvent, PayoutEvent, TicketEvent,
        AccountEvent, MessageEvent, WriterEvent
    )
    values: Set[str] = set()
    for enum in groups:
        values.update(enum.values)
    return values


def is_order_event(key: str) -> bool:
    return key in OrderEvent.values


def is_wallet_event(key: str) -> bool:
    return key in WalletEvent.values


def is_ticket_event(key: str) -> bool:
    return key in TicketEvent.values


def is_writer_event(key: str) -> bool:
    return key in WriterEvent.values


def is_account_event(key: str) -> bool:
    return key in AccountEvent.values


def is_file_event(key: str) -> bool:
    return key in FileEvent.values


def is_message_event(key: str) -> bool:
    return key in MessageEvent.values



__all__ = [
    "NotificationChannel", "NotificationType",
    "NotificationPriority", "DeliveryStatus",
    "NotificationCategory", "DigestType",
    # grouped events
    "OrderEvent", "FileEvent", "WalletEvent", "PayoutEvent",
    "TicketEvent", "AccountEvent", "MessageEvent", "WriterEvent",
    # helpers
    "all_event_values", "is_order_event", "is_wallet_event",
    "is_ticket_event", "is_writer_event", "is_account_event",
    "is_file_event", "is_message_event",
    "EventType", # legacy alias
]