from __future__ import annotations

from typing import Any

from class_management.constants import ClassOrderStatus


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

        if status in cls.TERMINAL_STATUSES and not available:
            blocked.append({"action": "lifecycle", "reason": "This class order is terminal."})

        return {
            "available_actions": sorted(set(available)),
            "blocked_actions": blocked,
        }
