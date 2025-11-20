# notifications_system/registry/event_priorities.py
"""
Event priorities for the notifications system.

Defines a simple mapping of event keys to priority labels and exposes
helpers to fetch/validate them. Priorities should align with your
NotificationPriority enum labels (lowercase): 'critical', 'high',
'medium', 'normal', 'low'.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# Allowed priority levels (lowercase).
PRIORITY_LEVELS = {"critical", "high", "medium", "normal", "low"}

# ---------------------------------------------------------------------
# Canonical priorities (deduped; lowercase values).
# If you add new keys, keep them lowercase dotted paths.
# ---------------------------------------------------------------------
EVENT_PRIORITIES: Dict[str, str] = {
    # Orders
    "order.late": "high",
    "order.completed": "normal",
    "order.reviewed": "low",
    "order.created": "normal",
    "order.on_hold": "high",
    "order.cancelled": "normal",
    "order.assigned": "normal",
    "order.preferred_writer_assigned": "normal",
    "order.refunded": "medium",
    "order.revised": "normal",
    "order.archived": "low",
    "order.paid": "medium",
    "order.in_progress": "normal",
    "order.unpaid": "high",
    "order.approved": "normal",
    "order.disputed": "high",
    "order.dispute_resolved": "normal",
    "order.dispute_appealed": "high",
    "order.dispute_closed": "normal",
    "order.reopened": "normal",
    "order.under_editing": "normal",
    "order.rated": "normal",
    "order.review_approved": "normal",
    "order.deadline_approaching": "critical",
    "order.deadline_passed": "high",
    "order.payment_failed": "high",
    "order.payment_successful": "normal",
    "order.payment_refunded": "normal",
    "order.payment_disputed": "high",
    "order.payment_settled": "normal",
    "order.payment_chargeback": "high",
    "order.payment_canceled": "normal",
    "order.payment_pending": "normal",
    "order.payment_verified": "normal",
    "order.payment_declined": "high",
    "order.payment_authorized": "normal",
    "order.payment_voided": "normal",
    "order.payment_partially_refunded": "normal",
    "order.payment_partially_charged_back": "high",
    "order.payment_partially_settled": "normal",
    "order.payment_partially_verified": "normal",
    "order.payment_partially_declined": "high",
    "order.payment_partially_authorized": "normal",
    "order.payment_partially_voided": "normal",
    "order.payment_partially_canceled": "normal",
    "order.payment_partially_pending": "normal",

    # Files (order.* and file.* both exist in your tree; keep both)
    "order.file_uploaded": "normal",
    "order.file_downloaded": "normal",
    "order.file_deleted": "low",
    "order.file_updated": "normal",
    "order.file_accessed": "normal",
    "order.file_shared": "normal",
    "order.file_archived": "low",
    "order.file_restored": "normal",
    "order.file_locked": "normal",
    "order.file_unlocked": "normal",
    "order.file_compressed": "normal",
    "order.file_extracted": "normal",
    "order.file_moved": "normal",

    "file.uploaded": "normal",
    "file.downloaded": "normal",
    "file.deleted": "low",
    "file.updated": "normal",
    "file.accessed": "normal",
    "file.shared": "normal",
    "file.archived": "low",
    "file.restored": "normal",
    "file.locked": "normal",
    "file.unlocked": "normal",
    "file.compressed": "normal",
    "file.extracted": "normal",
    "file.moved": "normal",

    # Documents
    "document.created": "normal",
    "document.updated": "normal",
    "document.deleted": "low",
    "document.review_requested": "normal",
    "document.review_completed": "normal",
    "document.approved": "normal",
    "document.rejected": "normal",
    "document.published": "normal",
    "document.archived": "low",

    # Users
    "user.registered": "normal",
    "user.login": "normal",
    "user.logout": "low",
    "user.password_reset_requested": "high",
    "user.password_reset_completed": "high",
    "user.email_changed": "normal",
    "user.profile_updated": "low",
    "user.password_changed": "high",
    "user.email_verified": "normal",
    "user.account_suspended": "high",
    "user.account_reactivated": "normal",
    "user.two_factor_enabled": "normal",
    "user.two_factor_disabled": "normal",
    "user.notification_preferences_updated": "low",
    "user.notification_preferences_reset": "low",
    "user.notification_preferences_assigned": "low",
    "user.notification_preferences_removed": "low",
    "user.notification_preferences_reset_requested": "low",
    "user.notification_preferences_reset_completed": "low",
    "user.account_deletion_requested": "high",
    "user.account_deletion_completed": "normal",
    "user.temporary_password_generated": "normal",
    "user.temporary_password_used": "normal",
    "user.temporary_password_expired": "normal",
    "user.temporary_password_reset": "normal",
    "user.temporary_password_invalidated": "normal",

    # Classes
    "class.created": "normal",
    "class.updated": "normal",

    # Special orders
    "special_order.created": "normal",
    "special_order.updated": "normal",
    "special_order.deleted": "low",
    "special_order.payment_received": "normal",
    "special_order.payment_failed": "high",
    "special_order.payment_refunded": "normal",
    "special_order.payment_successful": "normal",
    "special_order.payment_pending": "normal",
    "special_order.payment_verified": "normal",
    "special_order.payment_declined": "high",
    "special_order.payment_authorized": "normal",
    "special_order.payment_voided": "normal",
    "special_order.payment_partially_refunded": "normal",
    "special_order.payment_partially_charged_back": "high",
    "special_order.payment_partially_settled": "normal",
    "special_order.writer_assigned": "normal",
    "special_order.writer_unassigned": "normal",
    "special_order.writer_reassigned": "normal",
    "special_order.writer_feedback_requested": "normal",
    "special_order.writer_feedback_received": "normal",
    "special_order.milestone_created": "normal",
    "special_order.milestone_updated": "normal",
    "special_order.milestone_deleted": "low",
    "special_order.milestone_completed": "normal",

    # Wallet
    "wallet.transaction_created": "normal",
    "wallet.transaction_updated": "normal",
    "wallet.transaction_deleted": "low",
    "wallet.transaction_completed": "normal",
    "wallet.transaction_failed": "high",
    "wallet.transaction_refunded": "normal",
    "wallet.transaction_successful": "normal",
    "wallet.transaction_pending": "normal",
    "wallet.debited": "normal",  # fixed spelling
    "wallet.credited": "normal",
    "wallet.balance_updated": "normal",
    "wallet.balance_low": "high",

    # Payouts
    "payouts.created": "normal",
    "payouts.updated": "normal",
    "payouts.deleted": "low",
    "payouts.completed": "normal",
    "payouts.failed": "high",
    "payouts.refunded": "normal",
    "payouts.successful": "normal",
    "payouts.pending": "normal",
    "payouts.verified": "normal",
    "payouts.declined": "high",
    "payouts.authorized": "normal",
    "payouts.voided": "normal",
    "payouts.partially_refunded": "normal",
    "payouts.partially_charged_back": "high",
    "payouts.partially_settled": "normal",
    "payouts.partially_verified": "normal",
    "payouts.partially_declined": "high",
    "payouts.partially_authorized": "normal",
    "payouts.processing": "normal",
    "payouts.cancelled": "normal",
    "payouts.rolled_over": "normal",
}

# Compatibility aliases (typos/old keys -> canonical keys).
EVENT_KEY_ALIASES: Dict[str, str] = {
    "wallet.debitted": "wallet.debited",
    # add more aliases here if you fix keys later
}

# Optional fanout guidance (kept as-is, but documented).
EVENT_FANOUT_CONFIG: Dict[str, str] = {
    "order.assigned": "group_team",  # or "individual"
}


def normalize_event_key(event_key: str) -> str:
    """Return a canonical event key (apply alias mapping).

    Args:
        event_key: Raw event key (may contain legacy typos).

    Returns:
        Canonicalized event key.
    """
    return EVENT_KEY_ALIASES.get(event_key, event_key)


def get_priority(event_key: str) -> str:
    """Return the priority for an event key (defaults to 'normal').

    Args:
        event_key: Canonical or aliased event key.

    Returns:
        Priority label as lowercase string.
    """
    key = normalize_event_key(event_key)
    return EVENT_PRIORITIES.get(key, "normal")


def validate_priorities() -> List[Tuple[str, Optional[str]]]:
    """Validate priority mapping.

    Checks:
      * All priorities are within PRIORITY_LEVELS.
      * Alias targets exist in EVENT_PRIORITIES.

    Returns:
        A list of (error_message, offending_key) tuples.
        Empty list means OK.
    """
    errors: List[Tuple[str, Optional[str]]] = []

    for k, v in EVENT_PRIORITIES.items():
        if v not in PRIORITY_LEVELS:
            errors.append((f"Invalid priority '{v}' for '{k}'", k))

    for src, dst in EVENT_KEY_ALIASES.items():
        if dst not in EVENT_PRIORITIES:
            errors.append((f"Alias target missing: {src} -> {dst}", src))

    return errors


def get_fanout_strategy(event_key: str) -> Optional[str]:
    """Return a suggested fanout strategy for an event, if defined.

    Args:
        event_key: Canonical or aliased event key.

    Returns:
        String strategy or None.
    """
    key = normalize_event_key(event_key)
    return EVENT_FANOUT_CONFIG.get(key)