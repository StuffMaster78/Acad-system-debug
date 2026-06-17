"""Enums for the notification system."""
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class NotificationEvent(TextChoices):
    """
    All notification events in the system.

    Naming convention: {domain}.{action}
    Recipient notes show who receives each version where multiple
    recipients get different rendered content for the same event.

    Note: Auth transactional emails (signup, password reset etc.)
    are handled by the authentication app, not this system.
    """

    # Orders — most events have a client version and a writer version
    ORDER_CREATED = 'order.created', _('Order Created')
    ORDER_ASSIGNED = 'order.assigned', _(
        'Order Assigned') # writer + client receive
    # writer + client receive
    ORDER_UPDATED = 'order.updated', _('Order Updated')
    ORDER_APPROVED = 'order.approved', _('Order Approved')
    ORDER_COMPLETED = 'order.completed', _(
        'Order Completed') # writer + client receive
    ORDER_CANCELLED = 'order.cancelled', _(
        'Order Cancelled') # writer + client receive
    ORDER_REJECTED = 'order.rejected', _('Order Rejected')
    ORDER_ON_HOLD = 'order.on_hold', _('Order On Hold')
    ORDER_REOPENED = 'order.reopened', _(
        'Order Reopened') # writer + client receive
    ORDER_REASSIGNED = 'order.reassigned', _(
        'Order Reassigned') # writer receives
    ORDER_REVISION_REQUESTED = 'order.revision_requested', _(
        'Revision Requested') # writer receives
    ORDER_REVISION_COMPLETED = 'order.revision_completed', _(
        'Revision Completed') # writer + client receive
    ORDER_DISPUTED = 'order.disputed', _(
        'Order Disputed') # staff receives
    ORDER_DISPUTE_RESOLVED = 'order.dispute_resolved', _(
        'Dispute Resolved') # writer + client receive
    ORDER_DISPUTE_ESCALATED = 'order.dispute_escalated', _(
        'Dispute Escalated') # staff receives
    ORDER_DEADLINE_APPROACHING = 'order.deadline_approaching', _(
        'Deadline Approaching') # writer receives
    # writer receives
    ORDER_RATED = 'order.rated', _('Order Rated')
    ORDER_QA_REVIEW_READY = "order.qa_review_ready"
    ORDER_SUBMITTED = "order.submitted", _("Order Submitted")

    # Bid / writer-interest events
    ORDER_BID_PLACED = "order.bid.placed", _("Bid Placed")
    ORDER_BID_ACCEPTED = "order.bid.accepted", _("Bid Accepted")
    ORDER_BID_REJECTED = "order.bid.rejected", _("Bid Rejected")

    # Order adjustment workflow — scope increases, extra services, counters,
    # funding reminders, and staff escalation handling.
    ORDER_ADJUSTMENT_CREATED = "order.adjustment.created", _("Order Adjustment Created")
    ORDER_ADJUSTMENT_COUNTERED = "order.adjustment.countered", _("Order Adjustment Countered")
    ORDER_ADJUSTMENT_ACCEPTED = "order.adjustment.accepted", _("Order Adjustment Accepted")
    ORDER_ADJUSTMENT_DECLINED = "order.adjustment.declined", _("Order Adjustment Declined")
    ORDER_ADJUSTMENT_CANCELLED = "order.adjustment.cancelled", _("Order Adjustment Cancelled")
    ORDER_ADJUSTMENT_ESCALATED = "order.adjustment.escalated", _("Order Adjustment Escalated")
    ORDER_ADJUSTMENT_ESCALATION_RESOLVED = "order.adjustment.escalation_resolved", _("Order Adjustment Escalation Resolved")
    ORDER_ADJUSTMENT_PENDING_CLIENT_RESPONSE_REMINDER = "order.adjustment.pending_client_response_reminder", _("Order Adjustment Client Response Reminder")
    ORDER_ADJUSTMENT_PENDING_FUNDING_REMINDER = "order.adjustment.pending_funding_reminder", _("Order Adjustment Funding Reminder")
    ORDER_ADJUSTMENT_STAFF_VISIBILITY_REMINDER = "order.adjustment.staff_visibility_reminder", _("Order Adjustment Staff Visibility Reminder")

    # Cancellation request workflow
    ORDER_CANCELLATION_REQUESTED = "order.cancellation_requested", _("Cancellation Requested")
    ORDER_CANCELLATION_REJECTED = "order.cancellation_rejected", _("Cancellation Rejected")

    # Writer direct-assignment acceptance gate
    ORDER_ASSIGNMENT_ACCEPTED = "order.assignment_accepted", _("Assignment Accepted")
    ORDER_ASSIGNMENT_REJECTED = "order.assignment_rejected", _("Assignment Rejected")

    # Billing — installment lifecycle events
    BILLING_INSTALLMENT_DUE = "billing.installment.due", _("Installment Due")
    BILLING_INSTALLMENT_UPCOMING = "billing.installment.upcoming", _("Installment Upcoming")
    BILLING_INVOICE_SETTLED = "billing.invoice.settled", _("Invoice Settled")
    BILLING_INVOICE_ISSUED = "billing.invoice.issued", _("Invoice Issued")

    # Preferred writer invitation workflow
    ORDER_PREFERRED_WRITER_PENDING_REMINDER = "order.preferred_writer.pending_reminder", _("Preferred Writer Pending Reminder")
    ORDER_PREFERRED_WRITER_FALLBACK_TO_POOL = "order.preferred_writer.fallback_to_pool", _("Preferred Writer Fallback to Pool")
    ORDER_PREFERRED_WRITER_STAFF_VISIBILITY_REMINDER = "order.preferred_writer.staff_visibility_reminder", _("Preferred Writer Staff Visibility Reminder")

    # Payments / Wallet
    WALLET_CREDITED = 'wallet.credited', _('Wallet Credited')
    WALLET_DEBITED = 'wallet.debited', _('Wallet Debited')
    WALLET_BALANCE_LOW = 'wallet.balance_low', _('Wallet Balance Low')
    WALLET_TX_FAILED = 'wallet.tx_failed', _('Transaction Failed')
    WALLET_REFUND_INITIATED = 'wallet.refund_initiated', _('Refund Initiated')
    WALLET_REFUND_COMPLETED = 'wallet.refund_completed', _('Refund Completed')
    WALLET_CLIENT_FUNDED = 'wallet.client.funded', _('Client Wallet Funded')
    WALLET_CLIENT_DEBITED = 'wallet.client.debited', _(
        'Client Wallet Debited')
    WALLET_CLIENT_REFUNDED = (
        'wallet.client.refunded',
        _('Client Wallet Refunded'),
    )
    WALLET_WRITER_EARNING_POSTED = (
        'wallet.writer.earning_posted',
        _('Writer Earning Posted'),
    )
    WALLET_WRITER_BONUS_POSTED = (
        'wallet.writer.bonus_posted',
        _('Writer Bonus Posted'),
    )
    WALLET_WRITER_PENALTY_POSTED = (
        'wallet.writer.penalty_posted',
        _('Writer Penalty Posted'),
    )

    # Payouts and compensation — writer-specific
    PAYOUT_REQUESTED = 'payout.requested', _(
        'Payout Requested') # staff receives
    PAYOUT_PROCESSING = 'payout.processing', _(
        'Payout Processing') # writer receives
    PAYOUT_COMPLETED = 'payout.completed', _(
        'Payout Completed') # writer receives
    PAYOUT_FAILED = 'payout.failed', _(
        'Payout Failed') # writer receives
    PAYOUT_ROLLED_OVER = 'payout.rolled_over', _(
        'Payout Rolled Over') # writer receives
    COMPENSATION_PAYMENT_PROCESSING = (
        'compensation.payment_processing',
        _('Compensation Payment Processing'),
    )
    COMPENSATION_PAYMENT_PAID = (
        'compensation.payment_paid',
        _('Compensation Payment Paid'),
    )
    COMPENSATION_PAYMENT_ON_HOLD = (
        'compensation.payment_on_hold',
        _('Compensation Payment On Hold'),
    )
    COMPENSATION_FINE_APPLIED = (
        'compensation.fine_applied',
        _('Compensation Fine Applied'),
    )
    COMPENSATION_ADJUSTMENT_APPLIED = (
        'compensation.adjustment_applied',
        _('Compensation Adjustment Applied'),
    )

    # Writer management — staff acts, writer receives
    WRITER_APPROVED = 'writer.approved', _('Writer Approved')
    WRITER_REJECTED = 'writer.rejected', _('Writer Rejected')
    WRITER_SUSPENDED = 'writer.suspended', _('Writer Suspended')
    WRITER_REINSTATED = 'writer.reinstated', _('Writer Reinstated')
    WRITER_BANNED = 'writer.banned', _('Writer Banned')
    WRITER_UNBANNED = 'writer.unbanned', _('Writer Unbanned')
    WRITER_WARNING = 'writer.warning', _('Writer Warning')
    WRITER_STRIKED = 'writer.striked', _('Writer Striked')
    WRITER_PROBATION = 'writer.probation', _('Writer On Probation')
    WRITER_PROMOTED = 'writer.promoted', _('Writer Promoted')
    WRITER_DEMOTED = 'writer.demoted', _('Writer Demoted')
    WRITER_LEVEL_UP = 'writer.level_up', _('Writer Level Up')
    WRITER_BADGE_EARNED = 'writer.badge_earned', _('Badge Earned')

    # Tickets — one version for user, one for staff
    TICKET_CREATED = 'ticket.created', _(
        'Ticket Created') # staff receives
    TICKET_UPDATED = 'ticket.updated', _('Ticket Updated')
    TICKET_ASSIGNED = 'ticket.assigned', _(
        'Ticket Assigned') # staff receives
    TICKET_ESCALATED = 'ticket.escalated', _(
        'Ticket Escalated') # staff receives
    TICKET_RESOLVED = 'ticket.resolved', _(
        'Ticket Resolved') # user receives
    TICKET_CLOSED = 'ticket.closed', _('Ticket Closed')
    TICKET_REOPENED = 'ticket.reopened', _('Ticket Reopened')
    TICKET_COMMENT_ADDED = 'ticket.comment_added', _(
        'Comment Added') # user + staff receive

    # Account
    ACCOUNT_SUSPENDED = 'account.suspended', _('Account Suspended')
    ACCOUNT_BLACKLISTED = 'account.blacklisted', _('Account Blacklisted')
    ACCOUNT_REACTIVATED = 'account.reactivated', _('Account Reactivated')
    ACCOUNT_DELETION_REQUESTED = 'account.deletion_requested', _(
        'Deletion Requested')
    ACCOUNT_DELETION_SCHEDULED = 'account.deletion_scheduled', _(
        'Deletion Scheduled')
    ACCOUNT_VERIFIED = 'account.verified', _('Account Verified')
    ACCOUNT_LOGIN_NEW_DEVICE = 'account.login_new_device', _(
        'Login from New Device')
    ACCOUNT_PASSWORD_CHANGED = 'account.password_changed', _(
        'Password Changed')
    ACCOUNT_EMAIL_CHANGED = 'account.email_changed', _('Email Changed')
    ACCOUNT_TWO_FACTOR_ENABLED = 'account.2fa_enabled', _(
        'Two-Factor Enabled')
    ACCOUNT_TWO_FACTOR_DISABLED = 'account.2fa_disabled', _(
        'Two-Factor Disabled')

    # Files
    FILE_UPLOADED = 'file.uploaded', _('File Uploaded')
    FILE_UPDATED = 'file.updated', _('File Updated')
    FILE_DELETED = 'file.deleted', _('File Deleted')
    FILE_DELIVERY_UNLOCKED = 'file.delivery_unlocked', _('File Delivery Unlocked')

    # Loyalty and referrals
    LOYALTY_POINTS_AWARDED = 'loyalty.points_awarded', _(
        'Loyalty Points Awarded')
    LOYALTY_POINTS_CONVERTED = 'loyalty.points_converted', _(
        'Loyalty Points Converted')
    LOYALTY_TIER_UPGRADED = 'loyalty.tier_upgraded', _(
        'Loyalty Tier Upgraded')
    REFERRAL_REWARD_EARNED = 'referral.reward_earned', _(
        'Referral Reward Earned')

    # Messages
    MESSAGE_NEW = 'message.new', _('New Message')
    COMMUNICATION_MESSAGE_CREATED = (
        'communications.message.created',
        _('Communication Message Created'),
    )
    COMMUNICATION_MESSAGE_FLAGGED = (
        'communications.message.flagged',
        _('Communication Message Flagged'),
    )
    COMMUNICATION_THREAD_ESCALATED = (
        'communications.thread.escalated',
        _('Communication Thread Escalated'),
    )
    COMMUNICATION_LINK_REVIEW_CREATED = (
        'communications.link_review.created',
        _('Communication Link Review Created'),
    )

    # System / Admin — staff triggers, users receive
    SYSTEM_MAINTENANCE = 'system.maintenance', _('System Maintenance')
    SYSTEM_ALERT = 'system.alert', _('System Alert')
    SYSTEM_ANNOUNCEMENT = 'system.announcement', _('System Announcement')
    ADMIN_BROADCAST = 'system.broadcast', _('Admin Broadcast')

    WRITER_REWARD_ISSUED = "writer.reward.issued"
    WRITER_REWARD_REVOKED = "writer.reward.revoked"

    FILE_INFECTED_DETECTED = "file.infected_detected", "Infected file detected"

    # Class management
    CLASS_SUBMITTED = "class.submitted", _("Class Submitted")
    CLASS_WRITER_COMPENSATION_POSTED = (
        "class.writer_compensation_posted",
        _("Class Writer Compensation Posted"),
    )
    CLASS_TWO_FACTOR_REQUIRED = (
        "class.two_factor.required",
        _("Class Two-Factor Required"),
    )
    CLASS_PAYMENT_OVERDUE = "class.payment.overdue", _("Class Payment Overdue")

    # Scheduled digests — sent by the digest celery beat task
    SCHEDULED_DIGEST_DAILY = "scheduled.digest_daily", _("Daily Digest")
    SCHEDULED_DIGEST_WEEKLY = "scheduled.digest_weekly", _("Weekly Digest")

class NotificationChannel(TextChoices):
    """
    Delivery channels.
    Uncomment TELEGRAM when ready to integrate.
    """
    EMAIL = 'email', _('Email')
    IN_APP = 'in_app', _('In-App')
    # TELEGRAM = 'telegram', _('Telegram')


class NotificationPriority(TextChoices):
    LOW = 'low', _('Low')
    NORMAL = 'normal', _('Normal')
    HIGH = 'high', _('High')
    CRITICAL = 'critical', _('Critical')


class NotificationCategory(TextChoices):
    ORDER = 'order', _('Order')
    PAYMENT = 'payment', _('Payment')
    COMPENSATION = 'compensation', _('Compensation')
    WALLET = 'wallet', _('Wallet')
    WRITER = 'writer', _('Writer')
    ACCOUNT = 'account', _('Account')
    TICKET = 'ticket', _('Ticket')
    FILE = 'file', _('File')
    LOYALTY = 'loyalty', _('Loyalty')
    REFERRAL = 'referral', _('Referral')
    COMMUNICATION_MESSAGE = 'communication_message', _('Communicatin Message')
    CLASS = 'class', _('Class')
    SYSTEM = 'system', _('System')
    INFO = 'info', _('Info')


class TemplateScope(TextChoices):
    GLOBAL = 'global', 'Global'
    WEBSITE = 'website', 'Website Override'


class DeliveryStatus(TextChoices):
    PENDING = 'pending', _('Pending')
    QUEUED = 'queued', _('Queued')
    SENDING = 'sending', _('Sending')
    SENT = 'sent', _('Sent')
    RETRYING = 'retrying', _('Retrying')
    FAILED = 'failed', _('Failed')
    SKIPPED = 'skipped', _('Skipped')
    CANCELLED = 'cancelled', _('Cancelled')
    BOUNCED = 'bounced', _('Bounced')
    DLQ = 'dlq', _('Dead Letter Queue')
    UNDELIVERABLE = 'undeliverable', _('Undeliverable')
    # ADD: distinguishes suppressed addresses (bounce/complaint/unsubscribe)
    # from genuine delivery failures — visible separately in admin views.
    SUPPRESSED = 'suppressed', _('Suppressed')


class PreferenceSource(TextChoices):
    USER = 'user', 'Set by User'
    ADMIN = 'admin', 'Set by Admin'
    SYSTEM = 'system', 'System Default'


class DigestFrequency(TextChoices):
    IMMEDIATE = 'immediate', _('Immediate')
    HOURLY = 'hourly', _('Hourly')
    DAILY = 'daily', _('Daily')
    WEEKLY = 'weekly', _('Weekly')
    MONTHLY = 'monthly', _('Monthly')


# ===========================
# Helpers
# ===========================

def get_event_category(event_key: str) -> str:
    """Infer NotificationCategory from event key prefix."""
    prefix_map = {
        'order': NotificationCategory.ORDER,
        'wallet': NotificationCategory.WALLET,
        'payout': NotificationCategory.PAYMENT,
        'compensation': NotificationCategory.COMPENSATION,
        'ticket': NotificationCategory.TICKET,
        'account': NotificationCategory.ACCOUNT,
        'writer': NotificationCategory.WRITER,
        'file': NotificationCategory.FILE,
        'loyalty': NotificationCategory.LOYALTY,
        'referral': NotificationCategory.REFERRAL,
        'message': NotificationCategory.COMMUNICATION_MESSAGE,
        'communications': NotificationCategory.COMMUNICATION_MESSAGE,
        'class': NotificationCategory.CLASS,
        'system': NotificationCategory.SYSTEM,
        'scheduled': NotificationCategory.SYSTEM,
    }
    prefix = event_key.split('.')[0] if '.' in event_key else ''
    return prefix_map.get(prefix, NotificationCategory.INFO)


def is_valid_event(event_key: str) -> bool:
    """Check if an event key is registered."""
    return event_key in NotificationEvent.values


__all__ = [
    'NotificationEvent',
    'NotificationChannel',
    'NotificationPriority',
    'NotificationCategory',
    'DeliveryStatus',
    'DigestFrequency',
    'get_event_category',
    'is_valid_event',
]
