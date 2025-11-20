from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order
from orders.order_enums import OrderStatus  # you already have this
from websites.models import Website


ALLOWED_STAFF_ROLES = {"superadmin", "admin", "support"}
CLIENT_ROLE = "client"


def user_has_any_role(user, roles) -> bool:
    """Replace with your real role checker."""
    return getattr(user, "role", None) in roles


@dataclass(frozen=True)
class DeleteResult:
    order_id: int
    was_deleted: bool
    hard: bool


class OrderDeletionService:
    """Handles soft and hard deletion, plus restore, website-scoped."""

    def __init__(self, *, website: Website):
        self.website = website

    def _ensure_same_website(self, order: Order):
        if order.website_id != self.website.id:
            raise PermissionDenied("Cross-tenant access is not allowed.")

    def _ensure_can_soft_delete(self, *, user, order: Order):
        # Staff can soft-delete any order.
        if user_has_any_role(user, ALLOWED_STAFF_ROLES):
            return

        # Clients: only if unpaid.
        if getattr(user, "role", None) == CLIENT_ROLE:
            if order.user_id != user.id:
                raise PermissionDenied("Cannot delete another user's order.")
            if order.status != OrderStatus.UNPAID:
                raise PermissionDenied("Client can only delete unpaid orders.")
            return

        raise PermissionDenied("Insufficient privileges to delete order.")

    def _ensure_can_hard_delete(self, *, user):
        if not user_has_any_role(user, ALLOWED_STAFF_ROLES):
            raise PermissionDenied("Only staff can hard-delete orders.")

    @transaction.atomic
    def soft_delete(
        self, *, user, order: Order, reason: str = ""
    ) -> DeleteResult:
        """Soft delete and keep restorable."""
        self._ensure_same_website(order)
        self._ensure_can_soft_delete(user=user, order=order)

        if order.is_deleted:
            # Idempotent: already deleted
            return DeleteResult(order_id=order.id, was_deleted=False, hard=False)

        order.mark_deleted(user=user, reason=reason)
        order.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by",
            "delete_reason", "restored_at", "restored_by"
        ])

        # optional: audit log hook
        # AuditLogger.log(user, "order.soft_deleted", {...})

        return DeleteResult(order_id=order.id, was_deleted=True, hard=False)

    @transaction.atomic
    def restore(self, *, user, order: Order) -> int:
        """Restore a soft-deleted order."""
        self._ensure_same_website(order)

        if not order.is_deleted:
            raise ValidationError("Order is not deleted.")

        # Staff can always restore; client can restore only own order.
        if user_has_any_role(user, ALLOWED_STAFF_ROLES):
            pass
        elif getattr(user, "role", None) == CLIENT_ROLE:
            if order.user_id != user.id:
                raise PermissionDenied("Cannot restore another user's order.")
        else:
            raise PermissionDenied("Insufficient privileges to restore order.")

        order.mark_restored(user=user)
        order.save(update_fields=[
            "is_deleted", "restored_at", "restored_by"
        ])

        # optional: audit log hook
        # AuditLogger.log(user, "order.restored", {...})

        return order.id

    @transaction.atomic
    def hard_delete_by_id(self, *, user, order_id: int) -> DeleteResult:
        """Irreversible delete (DB row removal). Staff only."""
        self._ensure_can_hard_delete(user=user)

        try:
            order = Order.objects.select_for_update().get(
                id=order_id, website_id=self.website.id
            )
        except Order.DoesNotExist:
            # Idempotent: treat as already gone
            return DeleteResult(order_id=order_id, was_deleted=False, hard=True)

        # Optional safety net: forbid hard delete of PAID unless superadmin
        # if order.status != OrderStatus.UNPAID and user.role != "superadmin":
        #     raise PermissionDenied("Only superadmin can purge paid orders.")

        oid = order.id
        order.delete()
        # optional: audit log hook
        # AuditLogger.log(user, "order.hard_deleted", {"order_id": oid})

        return DeleteResult(order_id=oid, was_deleted=True, hard=True)