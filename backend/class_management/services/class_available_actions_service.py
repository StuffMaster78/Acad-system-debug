from __future__ import annotations

from typing import Any

from class_management.constants import ClassOrderStatus, ClassPaymentStatus


class ClassAvailableActionsService:
    """
    Role-aware action contract for class orders.

    The returned action ids intentionally match the viewset action names where
    an endpoint already exists.
    """

    TERMINAL_STATUSES = {
        ClassOrderStatus.COMPLETED,
        ClassOrderStatus.CANCELLED,
        ClassOrderStatus.ARCHIVED,
    }

    @classmethod
    def for_order(cls, *, class_order: Any, user: Any) -> dict[str, list[dict[str, str]] | list[str]]:
        available: list[str] = []
        blocked: list[dict[str, str]] = []
        status = getattr(class_order, "status", "")
        role = getattr(user, "role", "")
        is_staff = bool(getattr(user, "is_staff", False) or role in {"admin", "superadmin", "support", "editor"})
        is_client = getattr(getattr(class_order, "client", None), "pk", None) == getattr(user, "pk", None)

        if is_client:
            if status == ClassOrderStatus.DRAFT:
                available.extend(["submit", "cancel"])
            elif status not in cls.TERMINAL_STATUSES:
                blocked.append({"action": "submit", "reason": "Only draft class orders can be submitted."})

        if is_staff:
            if status == ClassOrderStatus.SUBMITTED:
                available.append("start_review")
            if getattr(class_order, "payment_status", "") in {
                ClassPaymentStatus.UNPAID,
                ClassPaymentStatus.PARTIALLY_PAID,
                ClassPaymentStatus.OVERDUE,
            } or status in {
                ClassOrderStatus.ACCEPTED,
                ClassOrderStatus.PENDING_PAYMENT,
                ClassOrderStatus.PARTIALLY_PAID,
            }:
                available.append("manual_mark_paid")
            if (
                status in {ClassOrderStatus.PAID, ClassOrderStatus.ASSIGNED}
                and getattr(class_order, "payment_status", "") == ClassPaymentStatus.PAID
            ):
                available.append("assign_writer")
            if status in {
                ClassOrderStatus.PAID,
                ClassOrderStatus.ASSIGNED,
                ClassOrderStatus.PAUSED,
            }:
                available.append("start_work")
            if status in {ClassOrderStatus.IN_PROGRESS, ClassOrderStatus.QUALITY_REVIEW}:
                available.append("complete")
            if status not in cls.TERMINAL_STATUSES:
                available.append("cancel")
            if status in {ClassOrderStatus.COMPLETED, ClassOrderStatus.CANCELLED}:
                available.append("archive")

            if status in {
                ClassOrderStatus.ACCEPTED,
                ClassOrderStatus.PENDING_PAYMENT,
                ClassOrderStatus.PARTIALLY_PAID,
            }:
                blocked.append({
                    "action": "assign_writer",
                    "reason": "Class must be fully paid before writer assignment.",
                })
            elif (
                status in {ClassOrderStatus.PAID, ClassOrderStatus.ASSIGNED, ClassOrderStatus.IN_PROGRESS}
                and getattr(class_order, "payment_status", "") != ClassPaymentStatus.PAID
            ):
                blocked.append({
                    "action": "assign_writer",
                    "reason": "Payment status is not paid, so writer assignment is blocked.",
                })

        if status in cls.TERMINAL_STATUSES and not available:
            blocked.append({"action": "lifecycle", "reason": "This class order is terminal."})

        return {
            "available_actions": sorted(set(available)),
            "blocked_actions": blocked,
        }
