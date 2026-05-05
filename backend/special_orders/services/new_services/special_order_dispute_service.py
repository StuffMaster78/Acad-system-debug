from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    DisputeResolutionType,
    DisputeStatus,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderDispute,
    SpecialOrderDisputeResolution,
    SpecialOrderRefundApplication,
)


class SpecialOrderDisputeService:
    """
    Manage disputes and dispute resolutions for special orders.

    Money movement is not performed here directly. If the resolution
    requires a refund, create the refund first through RefundService,
    then attach it to the resolution.
    """

    @classmethod
    @transaction.atomic
    def open_dispute(
        cls,
        *,
        special_order: SpecialOrder,
        opened_by,
        title: str,
        description: str,
        assigned_to=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderDispute:
        """
        Open a dispute for a special order.
        """
        if not title.strip():
            raise ValueError("Dispute title is required.")

        if not description.strip():
            raise ValueError("Dispute description is required.")

        return SpecialOrderDispute.objects.create(
            website=special_order.website,
            special_order=special_order,
            status=DisputeStatus.OPEN,
            title=title.strip(),
            description=description.strip(),
            opened_by=opened_by,
            assigned_to=assigned_to,
            opened_at=timezone.now(),
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def mark_under_review(
        cls,
        *,
        dispute: SpecialOrderDispute,
        reviewed_by,
    ) -> SpecialOrderDispute:
        """
        Move a dispute into review.
        """
        dispute = cls._lock_dispute(dispute=dispute)

        if dispute.status != DisputeStatus.OPEN:
            raise ValueError("Only open disputes can move under review.")

        dispute.status = DisputeStatus.UNDER_REVIEW
        dispute.assigned_to = reviewed_by
        dispute.save(
            update_fields=[
                "status",
                "assigned_to",
                "updated_at",
            ]
        )

        return dispute

    @classmethod
    @transaction.atomic
    def resolve_dispute(
        cls,
        *,
        dispute: SpecialOrderDispute,
        resolution_type: str,
        resolved_by,
        notes: str = "",
        amount: Decimal | None = None,
        refund_application: SpecialOrderRefundApplication | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderDisputeResolution:
        """
        Resolve a dispute.

        If resolution_type is refund-related, pass the already-created
        refund_application.
        """
        dispute = cls._lock_dispute(dispute=dispute)

        if dispute.status not in {
            DisputeStatus.OPEN,
            DisputeStatus.UNDER_REVIEW,
            DisputeStatus.AWAITING_CLIENT_RESPONSE,
            DisputeStatus.AWAITING_STAFF_RESPONSE,
        }:
            raise ValueError("Dispute cannot be resolved in current status.")

        cls._validate_resolution(
            dispute=dispute,
            resolution_type=resolution_type,
            amount=amount,
            refund_application=refund_application,
        )

        resolution = SpecialOrderDisputeResolution.objects.create(
            website=dispute.website,
            dispute=dispute,
            special_order=dispute.special_order,
            resolution_type=resolution_type,
            amount=amount,
            currency=dispute.special_order.currency,
            notes=notes,
            resolved_by=resolved_by,
            refund_application=refund_application,
            metadata=metadata or {},
        )

        dispute.status = DisputeStatus.RESOLVED
        dispute.resolved_at = timezone.now()
        dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "updated_at",
            ]
        )

        return resolution

    @classmethod
    @transaction.atomic
    def reject_dispute(
        cls,
        *,
        dispute: SpecialOrderDispute,
        rejected_by,
        reason: str,
    ) -> SpecialOrderDispute:
        """
        Reject a dispute with a required reason.
        """
        if not reason.strip():
            raise ValueError("Dispute rejection reason is required.")

        dispute = cls._lock_dispute(dispute=dispute)

        if dispute.status not in {
            DisputeStatus.OPEN,
            DisputeStatus.UNDER_REVIEW,
            DisputeStatus.AWAITING_CLIENT_RESPONSE,
            DisputeStatus.AWAITING_STAFF_RESPONSE,
        }:
            raise ValueError("Dispute cannot be rejected in current status.")

        dispute.status = DisputeStatus.REJECTED
        dispute.resolved_at = timezone.now()
        dispute.metadata = {
            **(dispute.metadata or {}),
            "rejected_by_id": getattr(rejected_by, "id", None),
            "rejection_reason": reason,
        }
        dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "metadata",
                "updated_at",
            ]
        )

        return dispute

    @staticmethod
    def _lock_dispute(
        *,
        dispute: SpecialOrderDispute,
    ) -> SpecialOrderDispute:
        """
        Lock dispute row.
        """
        return SpecialOrderDispute.objects.select_for_update().get(
            id=dispute.id,
            website=dispute.website,
        )

    @staticmethod
    def _validate_resolution(
        *,
        dispute: SpecialOrderDispute,
        resolution_type: str,
        amount: Decimal | None,
        refund_application: SpecialOrderRefundApplication | None,
    ) -> None:
        """
        Validate dispute resolution consistency.
        """
        refund_types = {
            DisputeResolutionType.PARTIAL_REFUND,
            DisputeResolutionType.FULL_REFUND,
            DisputeResolutionType.STORE_CREDIT,
        }

        if resolution_type not in {
            DisputeResolutionType.NO_ACTION,
            DisputeResolutionType.REVISION,
            DisputeResolutionType.PARTIAL_REFUND,
            DisputeResolutionType.FULL_REFUND,
            DisputeResolutionType.STORE_CREDIT,
            DisputeResolutionType.MANUAL_ADJUSTMENT,
        }:
            raise ValueError("Invalid dispute resolution type.")

        if resolution_type in refund_types and refund_application is None:
            raise ValueError(
                "Refund resolution requires a refund application."
            )

        if refund_application is not None:
            if refund_application.website_id != dispute.website_id:
                raise ValueError("Refund belongs to another tenant.")

            if refund_application.special_order_id != dispute.special_order_id:
                raise ValueError("Refund belongs to another special order.")

        if amount is not None and amount < Decimal("0.00"):
            raise ValueError("Resolution amount cannot be negative.")