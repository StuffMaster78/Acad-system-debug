# notifications_system/event_labels.py

"""
Maps event enums to human-friendly labels.
Keep this aligned with notifications_system.enums.*Event classes.
"""

from .enums import (
    OrderEvent, FileEvent, WalletEvent, PayoutEvent,
    TicketEvent, AccountEvent, MessageEvent, WriterEvent
)

EVENT_LABELS = {
    # --- Order Events ---
    OrderEvent.ASSIGNED: "Writer Assigned to Order",
    OrderEvent.ON_HOLD: "Order Put on Hold",
    OrderEvent.COMPLETED: "Order Marked as Completed",
    OrderEvent.CANCELLED: "Order Cancelled",
    OrderEvent.REJECTED: "Order Rejected",
    OrderEvent.UPDATED: "Order Updated",
    OrderEvent.CREATED: "New Order Created",
    OrderEvent.APPROVED: "Order Approved",
    OrderEvent.ARCHIVED: "Order Archived",
    OrderEvent.RESTORED: "Order Restored",
    OrderEvent.REOPENED: "Order Reopened",
    OrderEvent.REASSIGNED: "Writer Reassigned",
    OrderEvent.RATED: "Order Rated",
    OrderEvent.REVIEWED: "Order Reviewed",
    OrderEvent.PAYMENT_FAILED: "Payment Failed",
    OrderEvent.PAYMENT_SUCCESS: "Payment Successful",
    OrderEvent.REFUNDED: "Order Refunded",
    OrderEvent.ON_DISPUTE: "Order Entered Dispute",
    OrderEvent.DISPUTE_RESOLVED: "Dispute Resolved",
    OrderEvent.DISPUTE_ESCALATED: "Dispute Escalated",
    OrderEvent.DISPUTE_CLOSED: "Dispute Closed",
    OrderEvent.REVIEW_REQUESTED: "Client Asked to Review Order",
    OrderEvent.REVIEW_SUBMITTED: "Review Submitted",
    OrderEvent.REVIEW_APPROVED: "Review Approved",
    OrderEvent.REVIEW_REJECTED: "Review Rejected",

    # --- File Events ---
    FileEvent.UPLOADED: "File Uploaded",
    FileEvent.DELETED: "File Deleted",
    FileEvent.UPDATED: "File Updated",

    # --- Wallet Events ---
    WalletEvent.BALANCE_LOW: "Wallet Balance is Low",
    WalletEvent.CREDITED: "Wallet Credited",
    WalletEvent.DEBITED: "Wallet Debited",
    WalletEvent.TX_FAILED: "Wallet Transaction Failed",
    WalletEvent.TX_SUCCESS: "Wallet Transaction Succeeded",
    WalletEvent.REFUND_INITIATED: "Refund Initiated",
    WalletEvent.REFUND_COMPLETED: "Refund Completed",

    # --- Payout Events ---
    PayoutEvent.PROCESSING: "Payout Processing",
    PayoutEvent.COMPLETED: "Payout Completed",
    PayoutEvent.FAILED: "Payout Failed",
    PayoutEvent.CANCELLED: "Payout Cancelled",

    # --- Ticket Events ---
    TicketEvent.CREATED: "Support Ticket Created",
    TicketEvent.UPDATED: "Support Ticket Updated",
    TicketEvent.CLOSED: "Ticket Closed",
    TicketEvent.REOPENED: "Ticket Reopened",
    TicketEvent.ASSIGNED: "Ticket Assigned",
    TicketEvent.UNASSIGNED: "Ticket Unassigned",
    TicketEvent.ESCALATED: "Ticket Escalated",
    TicketEvent.RESOLVED: "Ticket Resolved",
    TicketEvent.COMMENT_ADDED: "Comment Added to Ticket",
    TicketEvent.COMMENT_UPDATED: "Comment Updated on Ticket",
    TicketEvent.COMMENT_DELETED: "Comment Deleted from Ticket",

    # --- Account Events ---
    AccountEvent.PASSWORD_RESET: "Password Reset Requested",
    AccountEvent.ACCOUNT_SUSPENDED: "Account Suspended",
    AccountEvent.USER_VERIFIED: "User Verified",
    AccountEvent.USER_UNVERIFIED: "User Unverified",
    AccountEvent.USER_BLACKLISTED: "User Blacklisted",
    AccountEvent.USER_UNBLACKLISTED: "User Removed from Blacklist",

    # --- Message Events ---
    MessageEvent.NEW_MESSAGE: "New Message",

    # --- Writer Events ---
    WriterEvent.REVIEWED: "Writer Reviewed",
    WriterEvent.SUSPENDED: "Writer Suspended",
    WriterEvent.PROBATION: "Writer Sent on Probation",
    WriterEvent.STRIKED: "Writer Received a Strike",
    WriterEvent.UNSTRIKED: "Strike Removed",
    WriterEvent.WARNING: "Writer Warning Issued",
    WriterEvent.BANNED: "Writer Banned",
    WriterEvent.UNBANNED: "Writer Unbanned",
    WriterEvent.REINSTATED: "Writer Reinstated",
    WriterEvent.REJECTED: "Writer Rejected",
    WriterEvent.APPROVED: "Writer Approved",
    WriterEvent.ON_HOLD: "Writer Put On Hold",
    WriterEvent.ON_PROBATION: "Writer On Probation",
    WriterEvent.PROMOTED: "Writer Promoted",
    WriterEvent.DEMOTED: "Writer Demoted",
    WriterEvent.REVIEW_REQUESTED: "Writer Review Requested",
    WriterEvent.REVIEW_SUBMITTED: "Writer Review Submitted",
    WriterEvent.REVIEW_APPROVED: "Writer Review Approved",
}

def get_event_label(event_key: str) -> str:
    """
    Return a human-friendly label for an event key, 
    or the key itself if unknown.
    """
    return EVENT_LABELS.get(event_key, event_key)

# Example usage:
# label = get_event_label(OrderEvent.CREATED)