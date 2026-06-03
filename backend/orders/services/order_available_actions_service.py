from __future__ import annotations

from typing import Any, Iterable

from django.core.exceptions import ValidationError

from orders.services.policies.order_cancellation_policy import (
    OrderCancellationPolicy,
)


STAFF_ROLES = {"admin", "superadmin", "support", "editor"}
REVIEW_ROLES = {"admin", "superadmin", "editor"}


class OrderAvailableActionsService:
    """
    Build a role-aware action list for order detail surfaces.

    The returned strings are API-facing action identifiers used by the
    frontend to decide which controls to show.
    """

    @classmethod
    def build_actions(
        cls,
        *,
        order: Any,
        user: Any,
        lifecycle: Any,
    ) -> list[str]:
        role = getattr(user, "role", None)
        status = str(getattr(order, "status", "") or "").lower()
        is_staff = role in STAFF_ROLES or bool(getattr(user, "is_staff", False))
        is_reviewer = role in REVIEW_ROLES or bool(getattr(user, "is_staff", False))
        is_client_owner = (
            getattr(order, "client_id", None) is not None
            and getattr(order, "client_id", None) == getattr(user, "pk", None)
        )
        is_current_writer = (
            getattr(lifecycle, "current_writer_id", None) is not None
            and getattr(lifecycle, "current_writer_id", None)
            == getattr(user, "pk", None)
        )

        actions: list[str] = []

        if is_staff:
            cls._extend_staff_actions(
                actions,
                order=order,
                status=status,
                lifecycle=lifecycle,
                is_reviewer=is_reviewer,
            )

        if is_client_owner:
            cls._extend_client_actions(
                actions,
                order=order,
                status=status,
                lifecycle=lifecycle,
            )

        if is_current_writer:
            cls._extend_writer_actions(
                actions,
                status=status,
                lifecycle=lifecycle,
            )

        return cls._dedupe(actions)

    @classmethod
    def _extend_staff_actions(
        cls,
        actions: list[str],
        *,
        order: Any,
        status: str,
        lifecycle: Any,
        is_reviewer: bool,
    ) -> None:
        if status in {"paid", "unpaid", "pending_payment"}:
            actions.append("route_to_staffing")

        if status in {"ready_for_staffing", "paid", "preferred_writer_pending"}:
            actions.append("assign_writer")

        if status in {"ready_for_staffing", "preferred_writer_pending", "assigned"}:
            actions.append("release_to_pool")

        if status == "in_progress":
            actions.append("submit_for_qa")

        if is_reviewer and status == "qa_review":
            actions.extend(["approve_delivery", "return_to_writer"])

        if status == "completed" and getattr(order, "approved_at", None) is None:
            actions.append("approve_order")

        if cls._can_request_revision(order=order, status=status):
            actions.append("request_revision")

        if cls._can_raise_dispute(status=status, lifecycle=lifecycle):
            actions.append("raise_dispute")

        if cls._can_cancel(order=order):
            actions.append("cancel_order")

        if cls._can_archive(order=order, lifecycle=lifecycle):
            actions.append("archive_order")

    @classmethod
    def _extend_client_actions(
        cls,
        actions: list[str],
        *,
        order: Any,
        status: str,
        lifecycle: Any,
    ) -> None:
        if status == "completed" and getattr(order, "approved_at", None) is None:
            actions.append("approve_order")

        if cls._can_request_revision(order=order, status=status):
            actions.append("request_revision")

        if cls._can_raise_dispute(status=status, lifecycle=lifecycle):
            actions.append("raise_dispute")

        if cls._can_cancel(order=order):
            actions.append("cancel_order")

    @classmethod
    def _extend_writer_actions(
        cls,
        actions: list[str],
        *,
        status: str,
        lifecycle: Any,
    ) -> None:
        if status == "in_progress" and not getattr(lifecycle, "has_active_hold", False):
            actions.append("submit_for_qa")

        if cls._can_raise_dispute(status=status, lifecycle=lifecycle):
            actions.append("raise_dispute")

    @staticmethod
    def _can_request_revision(*, order: Any, status: str) -> bool:
        return status in {"submitted", "completed"} and getattr(order, "approved_at", None) is None

    @staticmethod
    def _can_raise_dispute(*, status: str, lifecycle: Any) -> bool:
        return (
            status in {"in_progress", "submitted", "completed"}
            and not getattr(lifecycle, "has_active_dispute", False)
        )

    @staticmethod
    def _can_archive(*, order: Any, lifecycle: Any) -> bool:
        return (
            str(getattr(order, "status", "") or "").lower() == "completed"
            and getattr(order, "completed_at", None) is not None
            and getattr(order, "archived_at", None) is None
            and not getattr(lifecycle, "has_active_dispute", False)
        )

    @staticmethod
    def _can_cancel(*, order: Any) -> bool:
        try:
            OrderCancellationPolicy.validate_can_cancel(order=order)
        except ValidationError:
            return False
        return True

    @staticmethod
    def _dedupe(actions: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for action in actions:
            if action in seen:
                continue
            seen.add(action)
            result.append(action)
        return result
