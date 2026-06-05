from __future__ import annotations

from typing import Any

from special_orders.constants import SpecialOrderStatus


class SpecialOrderAvailableActionsService:
    """
    Role-aware action contract for special orders.

    Action ids map to existing API operations. Client-facing quote actions are
    included because they act on the latest sent quote, not the order row.
    """

    TERMINAL_STATUSES = {
        SpecialOrderStatus.CANCELLED,
        SpecialOrderStatus.APPROVED,
        SpecialOrderStatus.REFUNDED,
    }

    @classmethod
    def for_order(cls, *, special_order: Any, user: Any) -> dict[str, list[dict[str, str]] | list[str]]:
        status = getattr(special_order, "status", "")
        role = getattr(user, "role", "")
        is_staff = bool(
            getattr(user, "is_superuser", False)
            or role in {"admin", "superadmin", "support", "editor", "content_manager"}
        )
        is_client = getattr(getattr(special_order, "client", None), "pk", None) == getattr(user, "pk", None)
        is_writer = getattr(getattr(special_order, "writer", None), "pk", None) == getattr(user, "pk", None)

        available: list[str] = []
        blocked: list[dict[str, str]] = []

        if is_staff:
            if status in {SpecialOrderStatus.INQUIRY, SpecialOrderStatus.QUOTE_PENDING, SpecialOrderStatus.QUOTE_SENT}:
                available.append("create_quote")
            if status == SpecialOrderStatus.READY_FOR_STAFFING or (
                status == SpecialOrderStatus.ASSIGNED and getattr(special_order, "writer_id", None) is None
            ):
                available.append("assign_writer")
            if status == SpecialOrderStatus.ASSIGNED:
                available.append("start_work")
            if status == SpecialOrderStatus.SUBMITTED:
                available.append("mark_ready_for_delivery")
            if status in {SpecialOrderStatus.SUBMITTED, SpecialOrderStatus.READY_FOR_DELIVERY}:
                available.append("complete_order")
            if status == SpecialOrderStatus.COMPLETED:
                available.append("approve_order")
            if status in {SpecialOrderStatus.SUBMITTED, SpecialOrderStatus.READY_FOR_DELIVERY, SpecialOrderStatus.COMPLETED}:
                available.append("request_revision")
            if status == SpecialOrderStatus.ON_HOLD:
                available.append("release_hold")
            elif status not in cls.TERMINAL_STATUSES:
                available.append("hold_order")
            if status not in cls.TERMINAL_STATUSES and status != SpecialOrderStatus.ON_HOLD:
                available.append("cancel_order")

        if is_writer:
            if status == SpecialOrderStatus.ASSIGNED:
                available.append("start_work")
            if status in {SpecialOrderStatus.IN_PROGRESS, SpecialOrderStatus.ON_REVISION}:
                available.append("submit_work")
            if status == SpecialOrderStatus.REVISION_REQUESTED:
                available.append("start_revision")

        if is_client:
            if status == SpecialOrderStatus.QUOTE_SENT:
                available.extend(["accept_quote", "reject_quote"])
            if status in {SpecialOrderStatus.SUBMITTED, SpecialOrderStatus.READY_FOR_DELIVERY, SpecialOrderStatus.COMPLETED}:
                available.extend(["approve_order", "request_revision"])

        if status == SpecialOrderStatus.ON_HOLD:
            blocked.append({"action": "work", "reason": "This special order is on hold."})
        elif status in cls.TERMINAL_STATUSES and not available:
            blocked.append({"action": "lifecycle", "reason": "This special order is terminal."})

        return {
            "available_actions": sorted(set(available)),
            "blocked_actions": blocked,
        }
