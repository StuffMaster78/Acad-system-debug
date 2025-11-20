"""Handles soft/hard deletion and restoration of discounts with admin control."""

import logging
from django.core.exceptions import PermissionDenied
from discounts.models import Discount
from django.utils import timezone

logger = logging.getLogger(__name__)


class DiscountSoftDeleteService:
    """
    Provides methods to soft/hard delete and restore discounts.
    Enforces admin/superadmin permissions.
    """

    def __init__(self, user):
        """
        Initialize the service with the current user.

        Args:
            user (User): The user performing the action.
        """
        self.user = user

    def soft_delete_discount(self, discount):
        """
        Soft delete a single discount by marking it as deleted.

        Args:
            discount (Discount): The discount to soft delete.

        Raises:
            PermissionDenied: If user is not staff.
        """
        if not self.user.is_staff:
            raise PermissionDenied(
                "Only admins can soft delete discounts."
            )

        if discount.is_deleted:
            logger.warning(
                f"Discount {discount.code} is already soft deleted."
            )
            return

        discount.is_deleted = True
        discount.deleted_at = timezone.now()
        discount.save(update_fields=["is_deleted", "deleted_at"])
        logger.info(
            f"User {self.user.username} soft deleted discount {discount.code} at {discount.deleted_at}."
        )

    def hard_delete_discount(self, discount):
        """
        Hard delete a discount if it has been soft deleted.

        Args:
            discount (Discount): The discount to permanently delete.

        Raises:
            PermissionDenied: If user is not superuser.
        """
        if not self.user.is_superuser or not self.user.is_staff:
            raise PermissionDenied(
                "Only superadmins and admins can hard delete discounts."
            )

        if not discount.is_deleted:
            logger.warning(
                f"Discount {discount.code} must be soft deleted before hard delete."
            )
            return

        discount.delete()
        logger.info(
            f"User {self.user.username} hard deleted discount {discount.code} at {timezone.now()}."
        )

    def soft_delete_discounts(self, queryset):
        """
        Soft delete multiple discounts.

        Args:
            queryset (QuerySet): The discounts to soft delete.

        Raises:
            PermissionDenied: If user is not staff.
        """
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can soft delete discounts.")

        if not queryset.exists():
            logger.warning("No discounts found to soft delete.")
            return

        count = queryset.update(is_deleted=True)
        logger.info(f"Soft deleted {count} discounts.")

    def hard_delete_discounts(self, queryset):
        """
        Hard delete multiple already-soft-deleted discounts.

        Args:
            queryset (QuerySet): The discounts to hard delete.

        Raises:
            PermissionDenied: If user is not superuser.
        """
        if not self.user.is_superuser:
            raise PermissionDenied("Only superadmins can hard delete discounts.")

        if not queryset.exists():
            logger.warning("No discounts found to hard delete.")
            return

        soft_deleted_qs = queryset.filter(is_deleted=True)
        count = soft_deleted_qs.count()
        soft_deleted_qs.delete()

        logger.info(f"Hard deleted {count} discounts.")

    def restore_discount(self, discount):
        """
        Restore a soft-deleted discount.

        Args:
            discount (Discount): The discount to restore.

        Raises:
            PermissionDenied: If user is not staff.
        """
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can restore discounts.")

        if not discount.is_deleted:
            logger.warning(f"Discount {discount.code} is not deleted.")
            return

        discount.is_deleted = False
        discount.deleted_at = None
        discount.save(update_fields=["is_deleted", "deleted_at"])

        logger.info(
            f"User {self.user.username} restored discount {discount.code} at {timezone.now()}."
        )

    def restore_discounts(self, queryset):
        """
        Restore multiple soft-deleted discounts.

        Args:
            queryset (QuerySet): The discounts to restore.

        Raises:
            PermissionDenied: If user is not staff.
        """
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can restore discounts.")

        soft_deleted_qs = queryset.filter(is_deleted=True)

        if not soft_deleted_qs.exists():
            logger.warning("No soft-deleted discounts found to restore.")
            return

        count = soft_deleted_qs.update(is_deleted=False)
        logger.info(f"Restored {count} discounts.")