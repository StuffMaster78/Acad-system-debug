from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from files_management.enums import (
    DeliveryGuardBlockReason,
    DeliveryStatus,
    FilePurpose,
    FileScanStatus,
)
from files_management.exceptions import FileDeliveryBlocked, FileNotAvailable
from files_management.models.file_attachment import FileAttachment
from files_management.models.file_delivery_guard_result import (
    FileDeliveryGuardResult,
)

log = logging.getLogger(__name__)

# Scan statuses that mean the file is safe to download.
_SCAN_PASSED = {FileScanStatus.CLEAN, FileScanStatus.PASSED, FileScanStatus.SKIPPED}

# Purposes that require a delivery guard check before download.
GUARDED_PURPOSES = {
    FilePurpose.ORDER_FINAL,
    FilePurpose.SPECIAL_ORDER_MILESTONE,
}


class FileDeliveryGuardService:
    """
    Controls whether a client is allowed to download a final or milestone
    file.

    Guard checks are always recorded as FileDeliveryGuardResult rows so
    the UI can display the correct locked state and ops can audit access
    decisions.

    This service does not perform access control (role/visibility). That
    is FileAccessService's job. The delivery guard runs after access is
    confirmed and answers: "the user is allowed to act on this file, but
    is the delivery actually ready and paid for?"

    Responsibilities:
        1. Check scan status — file must pass before delivery.
        2. Check submission status — writer must have submitted the file.
        3. Check outstanding balance — client must have paid in full.
        4. Submit a file as the delivery candidate (flips is_submitted).
        5. Re-evaluate all guarded attachments when payment arrives.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def check(
        cls,
        *,
        attachment: FileAttachment,
        user=None,
        order=None,
    ) -> FileDeliveryGuardResult:
        """
        Run the delivery guard for a file attachment.

        Records the outcome and returns the guard result. Raises nothing —
        callers decide whether to raise FileDeliveryBlocked based on the
        result.

        Args:
            attachment: The file attachment being downloaded.
            user:       The user requesting the download (for audit).
            order:      Domain order object, used to check payment balance.

        Returns:
            FileDeliveryGuardResult with result=ALLOWED or BLOCKED.
        """
        try:
            result, blocked_reason, amount_due = cls._evaluate(
                attachment=attachment,
                order=order,
            )
        except Exception as exc:
            log.exception(
                "Delivery guard evaluation error attachment=%s: %s",
                attachment.pk,
                exc,
            )
            result = FileDeliveryGuardResult.RESULT_BLOCKED
            blocked_reason = DeliveryGuardBlockReason.GUARD_ERROR
            amount_due = None

        now = timezone.now()
        guard_result = FileDeliveryGuardResult.objects.create(
            attachment=attachment,
            checked_by=user,
            result=result,
            blocked_reason=blocked_reason if result == FileDeliveryGuardResult.RESULT_BLOCKED else "",
            amount_due=amount_due,
            unlocked_at=now if result == FileDeliveryGuardResult.RESULT_ALLOWED else None,
        )

        return guard_result

    @classmethod
    @transaction.atomic
    def check_and_raise(
        cls,
        *,
        attachment: FileAttachment,
        user=None,
        order=None,
    ) -> FileDeliveryGuardResult:
        """
        Run the guard and raise FileDeliveryBlocked if access is denied.

        Use this in download flows where a blocked result should abort
        immediately.
        """
        guard_result = cls.check(
            attachment=attachment,
            user=user,
            order=order,
        )
        if guard_result.is_blocked:
            raise FileDeliveryBlocked(
                blocked_reason=guard_result.blocked_reason,
                amount_due=guard_result.amount_due,
            )
        return guard_result

    @classmethod
    @transaction.atomic
    def submit_as_final(
        cls,
        *,
        attachment: FileAttachment,
        submitted_by,
        on_behalf_of=None,
        reason: str = "",
    ) -> FileAttachment:
        """
        Mark an attachment as the submitted delivery candidate.

        Validates:
            1. The attachment purpose is a guarded deliverable type.
            2. The managed file scan has passed.
            3. The file is not already submitted.

        Args:
            attachment:    FileAttachment to submit.
            submitted_by:  Actor performing the submit action.
            on_behalf_of:  Writer the staff member is acting for.
            reason:        Required when submitting on behalf of a writer.

        Returns:
            Updated FileAttachment.

        Raises:
            FileNotAvailable: If the file cannot be submitted.
        """
        if attachment.purpose not in GUARDED_PURPOSES:
            raise FileNotAvailable(
                f"Only {', '.join(GUARDED_PURPOSES)} files can be submitted "
                f"as delivery. Got: {attachment.purpose}"
            )

        if attachment.is_submitted:
            raise FileNotAvailable("This file has already been submitted.")

        managed_file = attachment.managed_file
        if managed_file is None:
            raise FileNotAvailable(
                "External links cannot be submitted as deliveries."
            )

        if managed_file.scan_status not in _SCAN_PASSED:
            raise FileNotAvailable(
                f"File cannot be submitted — scan status is "
                f"'{managed_file.scan_status}'. Wait for a clean scan result."
            )

        if on_behalf_of is not None and not reason:
            raise FileNotAvailable(
                "A reason is required when submitting on behalf of a writer."
            )

        now = timezone.now()
        attachment.is_submitted = True
        attachment.delivery_status = DeliveryStatus.SUBMITTED
        attachment.submitted_by = submitted_by
        attachment.submitted_on_behalf_of = on_behalf_of
        attachment.submission_reason = reason
        attachment.submitted_at = now
        attachment.save(update_fields=[
            "is_submitted",
            "delivery_status",
            "submitted_by",
            "submitted_on_behalf_of",
            "submission_reason",
            "submitted_at",
            "updated_at",
        ])

        log.info(
            "File submitted as delivery attachment=%s submitted_by=%s "
            "on_behalf_of=%s",
            attachment.pk,
            getattr(submitted_by, "pk", None),
            getattr(on_behalf_of, "pk", None),
        )

        return attachment

    @classmethod
    def unlock_after_payment(cls, *, order) -> list[FileAttachment]:
        """
        Re-evaluate all guarded attachments for an order after payment.

        Called by the payment service after a successful payment. Flips
        delivery_status to APPROVED on attachments that now pass the guard
        and fires the unlock notification.

        Returns:
            List of attachments that became unlocked.
        """
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(
            order, for_concrete_model=False
        )
        attachments = FileAttachment.objects.filter(
            content_type=content_type,
            object_id=order.pk,
            purpose__in=list(GUARDED_PURPOSES),
            is_submitted=True,
            is_active=True,
        ).select_related("managed_file")

        unlocked = []
        for attachment in attachments:
            try:
                guard_result = cls.check(
                    attachment=attachment,
                    order=order,
                )
                if guard_result.is_allowed:
                    attachment.delivery_status = DeliveryStatus.APPROVED
                    attachment.save(update_fields=["delivery_status", "updated_at"])
                    unlocked.append(attachment)
                    cls._notify_unlocked(order=order, attachment=attachment)
            except Exception as exc:
                log.exception(
                    "unlock_after_payment: guard check failed "
                    "attachment=%s order=%s: %s",
                    attachment.pk,
                    getattr(order, "pk", None),
                    exc,
                )

        return unlocked

    # ------------------------------------------------------------------
    # Internal evaluation
    # ------------------------------------------------------------------

    @classmethod
    def _evaluate(
        cls,
        *,
        attachment: FileAttachment,
        order=None,
    ) -> tuple[str, str, Optional[Decimal]]:
        """
        Return (result, blocked_reason, amount_due) for an attachment.
        """
        managed_file = attachment.managed_file

        # 1. Scan must pass.
        if managed_file is not None:
            if managed_file.scan_status not in _SCAN_PASSED:
                return (
                    FileDeliveryGuardResult.RESULT_BLOCKED,
                    DeliveryGuardBlockReason.SCAN_PENDING
                    if managed_file.scan_status in {
                        FileScanStatus.NOT_SCANNED,
                        FileScanStatus.QUEUED,
                        FileScanStatus.SCANNING,
                    }
                    else DeliveryGuardBlockReason.SCAN_FAILED,
                    None,
                )

        # 2. File must be submitted.
        if not attachment.is_submitted:
            return (
                FileDeliveryGuardResult.RESULT_BLOCKED,
                DeliveryGuardBlockReason.NOT_SUBMITTED,
                None,
            )

        # 3. Delivery must not be rejected by staff.
        if attachment.delivery_status == DeliveryStatus.REJECTED:
            return (
                FileDeliveryGuardResult.RESULT_BLOCKED,
                DeliveryGuardBlockReason.REJECTED,
                None,
            )

        # 4. Outstanding balance check.
        if order is not None:
            amount_due = cls._get_outstanding_balance(order=order)
            if amount_due is not None and amount_due > 0:
                return (
                    FileDeliveryGuardResult.RESULT_BLOCKED,
                    DeliveryGuardBlockReason.BALANCE_DUE,
                    amount_due,
                )

        return FileDeliveryGuardResult.RESULT_ALLOWED, "", None

    @staticmethod
    def _get_outstanding_balance(*, order) -> Optional[Decimal]:
        """
        Return the outstanding balance for an order, or None if unknown.

        Tries a lazy import of the order payment service. Returns None on
        any failure so the guard degrades gracefully rather than blocking.
        """
        try:
            from orders.services.policies.order_payment_guard import (
                OrderPaymentGuard,
            )
            return OrderPaymentGuard.get_outstanding_balance(order=order)
        except ImportError:
            pass
        except Exception as exc:
            log.warning(
                "_get_outstanding_balance: failed for order=%s: %s",
                getattr(order, "pk", None),
                exc,
            )
        return None

    @staticmethod
    def _notify_unlocked(*, order, attachment: FileAttachment) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            client = getattr(order, "client", None)
            if client is None:
                return
            NotificationService.notify(
                event_key="file.delivery_unlocked",
                recipient=client,
                website=order.website,
                context={
                    "order_id": getattr(order, "pk", None),
                    "attachment_id": attachment.pk,
                },
            )
        except Exception as exc:
            log.warning(
                "_notify_unlocked: failed for attachment=%s: %s",
                attachment.pk,
                exc,
            )
