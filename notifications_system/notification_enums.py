from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices
from enum import IntEnum


class NotificationType(TextChoices):
    IN_APP = "in_app", _("In App")
    EMAIL = "email", _("Email")
    SMS = "sms", _("SMS")
    WEBSOCKET = "ws", _("Websocket")
    PUSH = "push", _("Push")
    WEBHOOK = "webhook", _("Webhook")
    SYSTEM = "system", _("System")


class DigestType(TextChoices):
    DAILY = "daily_summary", _("Daily Summary")
    WEEKLY = "weekly_summary", _("Weekly Summary")
    CRITICAL = "critical_alerts", _("Critical Alerts")


class NotificationCategory(TextChoices):
    INFO = "info", _("Info")
    WARNING = "warning", _("Warning")
    ERROR = "error", _("Error")
    ANNOUNCEMENT = "announcement", _("Announcement")
    NEWS = "news", _("News")


class NotificationPriority(IntEnum):
    EMERGENCY = 1
    HIGH = 2
    MEDIUM_HIGH = 3
    NORMAL = 5
    LOW = 7
    PASSIVE = 10

    @classmethod
    def choices(cls):
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]


class DeliveryStatus(TextChoices):
    PENDING = "pending", _("Pending")
    SENT = "sent", _("Sent")
    FAILED = "failed", _("Failed")
    DELAYED = "delayed", _("Delayed")
    QUEUED = "queued", _("Queued")
    RETRY = "retry", _("Retry")
    TIMEOUT = "timeout", _("Timeout")


class EventType(TextChoices):
    ORDER_ASSIGNED = "order_assigned", _("Order Assigned")
    ORDER_ON_HOLD = "order_on_hold", _("Order On Hold")
    ORDER_COMPLETED = "order_completed", _("Order Completed")
    ORDER_CANCELLED = "order_cancelled", _("Order Cancelled")
    ORDER_REJECTED = "order_rejected", _("Order Rejected")
    ORDER_UPDATED = "order_updated", _("Order Updated")
    ORDER_CREATED = "order_created", _("Order Created")
    ORDER_PAYMENT_FAILED = "order_payment_failed", _("Order Payment Failed")
    ORDER_PAYMENT_SUCCESS = "order_payment_success", _("Order Payment Success")
    ORDER_REFUNDED = "order_refunded", _("Order Refunded")
    ORDER_ON_DISPUTE = "order_on_dispute", _("Order On Dispute")
    ORDER_DISPUTE_RESOLVED = "order_dispute_resolved", _("Order Dispute Resolved")
    ORDER_DISPUTE_ESCALATED = "order_dispute_escalated", _("Order Dispute Escalated")
    ORDER_DISPUTE_CLOSED = "order_dispute_closed", _("Order Dispute Closed")
    ORDER_REVIEW_REQUESTED = "order_review_requested", _("Order Review Requested")
    ORDER_REVIEW_SUBMITTED = "order_review_submitted", _("Order Review Submitted")
    ORDER_REVIEW_APPROVED = "order_review_approved", _("Order Review Approved")
    ORDER_REVIEW_REJECTED = "order_review_rejected", _("Order Review Rejected")
    ORDER_ARCHIVED = "order_archived", _("Order Archived")
    ORDER_RESTORED = "order_restored", _("Order Restored")
    ORDER_REASSIGNED = "order_reassigned", _("Order Reassigned")
    ORDER_REOPENED = "order_reopened", _("Order Reopened")
    ORDER_APPROVED = "order_approved", _("Order Approved")
    FILE_UPLOADED = "file_uploaded", _("File Uploaded")
    FILE_DELETED = "file_deleted", _("File Deleted")
    WALLET_BALANCE_LOW = "wallet_balance_low", _("Wallet Balance Low")
    WALLET_CREDITED = "wallet_credited", _("Wallet Credited")
    WALLET_DEBITED = "wallet_debited", _("Wallet Debited")
    WALLET_TRANSACTION_FAILED = "wallet_transaction_failed", _("Wallet Transaction Failed")
    WALLET_TRANSACTION_SUCCESS = "wallet_transaction_success", _("Wallet Transaction Success")
    WALLET_REFUND_INITIATED = "wallet_refund_initiated", _("Wallet Refund Initiated")
    WALLET_REFUND_COMPLETED = "wallet_refund_completed", _("Wallet Refund Completed")
    PAYOUT_PROCESSING = "payout_processing", _("Payout Processing")
    PAYOUT_COMPLETED = "payout_completed", _("Payout Completed")
    PAYOUT_FAILED = "payout_failed", _("Payout Failed")
    PAYOUT_CANCELLED = "payout_cancelled", _("Payout Cancelled")
    TICKET_CREATED = "ticket_created", _("Ticket Created")
    TICKET_UPDATED = "ticket_updated", _("Ticket Updated")
    TICKET_CLOSED = "ticket_closed", _("Ticket Closed")
    TICKET_REOPENED = "ticket_reopened", _("Ticket Reopened")
    TICKET_COMMENT_ADDED = "ticket_comment_added", _("Ticket Comment Added")
    TICKET_COMMENT_UPDATED = "ticket_comment_updated", _("Ticket Comment Updated")
    TICKET_COMMENT_DELETED = "ticket_comment_deleted", _("Ticket Comment Deleted")
    TICKET_ASSIGNED = "ticket_assigned", _("Ticket Assigned")
    TICKET_UNASSIGNED = "ticket_unassigned", _("Ticket Unassigned")
    TICKET_ESCALATED = "ticket_escalated", _("Ticket Escalated")
    TICKET_RESOLVED = "ticket_resolved", _("Ticket Resolved")
    FEEDBACK_RECEIVED = "feedback_received", _("Feedback Received")
    PASSWORD_RESET = "password_reset", _("Password Reset")
    ACCOUNT_SUSPENDED = "account_suspended", _("Account Suspended")
    NEW_MESSAGE = "new_message", _("New Message")
    ORDER_RATED = "order_rated", _("Order Rated")
    ORDER_REVIEWED = "order_reviewed", _("Order Reviewed")
    WRITER_REVIEWED = "writer_reviewed", _("Writer Reviewed")
    ORDER_REASSIGNMENT_REQUESTED = "order_reassignment_requested", _("Order Reassignment Requested")
    ORDER_REASSIGNMENT_APPROVED = "order_reassignment_approved", _("Order Reassignment Approved")
    WRITER_SUSPENDED = "writer_suspended", _("Writer Suspended")
    WRITER_SENT_ON_PROBATION = "writer_sent_on_probation", _("Writer Sent on Probation")
    USER_BLACKLISTED = "user_blacklisted", _("User Blacklisted")
    USER_UNBLACKLISTED = "user_unblacklisted", _("User Unblacklisted")
    USER_VERIFIED = "user_verified", _("User Verified")
    USER_UNVERIFIED = "user_unverified", _("User Unverified")
    WRITER_STRIKED = "writer_striked", _("Writer Striked")
    WRITER_UNSTRIKED = "writer_unstriked", _("Writer Unstriked")
    WRITER_WARNING = "writer_warning", _("Writer Warning")
    WRITER_BANNED = "writer_banned", _("Writer Banned")
    WRITER_UNBANNED = "writer_unbanned", _("Writer Unbanned")
    WRITER_REINSTATED = "writer_reinstated", _("Writer Reinstated")
    WRITER_REJECTED = "writer_rejected", _("Writer Rejected")
    WRITER_APPROVED = "writer_approved", _("Writer Approved")
    WRITER_ON_HOLD = "writer_on_hold", _("Writer On Hold")
    WRITER_ON_PROBATION = "writer_on_probation", _("Writer On Probation")
    WRITER_PROMOTED = "writer_promoted", _("Writer Promoted")
    WRITER_DEMOTED = "writer_demoted", _("Writer Demoted")
    WRITER_REVIEW_REQUESTED = "writer_review_requested", _("Writer Review Requested")
    WRITER_REVIEW_SUBMITTED = "writer_review_submitted", _("Writer Review Submitted")
    WRITER_REVIEW_APPROVED = "writer_review_approved", _("Writer Review Approved")

    