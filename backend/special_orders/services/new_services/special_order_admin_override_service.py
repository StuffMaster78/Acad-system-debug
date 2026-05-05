from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    AdminOverrideStatus,
    AdminOverrideType,
    DeliveryCheckpointStatus,
    PaymentApplicationSource,
    SpecialOrderStatus,
)
from special_orders.models.special_order import (
    SpecialOrder,
)
from special_orders.models.overrides import (
    SpecialOrderAdminOverride,
)
from special_orders.services.new_services.special_order_payment_application_service import (
    SpecialOrderPaymentApplicationService,
)
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderAdminOverrideService:
    """
    Manage dangerous admin overrides for special orders.

    Overrides record authority and reason. Actual workflow or funding
    changes still go through the correct domain services.
    """

    ADMIN_ROLES = {
        "admin",
        "superadmin",
    }

    @classmethod
    @transaction.atomic
    def request_override(
        cls,
        *,
        special_order: SpecialOrder,
        override_type: str,
        requested_by,
        reason: str,
        amount: Decimal | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderAdminOverride:
        """
        Request an admin override.
        """
        cls._validate_admin(actor=requested_by)
        cls._validate_override_type(override_type=override_type)

        if not reason.strip():
            raise ValueError("Override reason is required.")

        return SpecialOrderAdminOverride.objects.create(
            website=special_order.website,
            special_order=special_order,
            override_type=override_type,
            status=AdminOverrideStatus.PENDING,
            reason=reason.strip(),
            amount=amount,
            currency=special_order.currency,
            requested_by=requested_by,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def approve_override(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        approved_by,
    ) -> SpecialOrderAdminOverride:
        """
        Approve a pending override.
        """
        cls._validate_admin(actor=approved_by)

        override = cls._lock_override(override=override)

        if override.status != AdminOverrideStatus.PENDING:
            raise ValueError("Only pending overrides can be approved.")

        override.status = AdminOverrideStatus.APPROVED
        override.approved_by = approved_by
        override.approved_at = timezone.now()
        override.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_at",
                "updated_at",
            ]
        )

        return override

    @classmethod
    @transaction.atomic
    def reject_override(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        rejected_by,
        reason: str,
    ) -> SpecialOrderAdminOverride:
        """
        Reject a pending override.
        """
        cls._validate_admin(actor=rejected_by)

        if not reason.strip():
            raise ValueError("Override rejection reason is required.")

        override = cls._lock_override(override=override)

        if override.status != AdminOverrideStatus.PENDING:
            raise ValueError("Only pending overrides can be rejected.")

        override.status = AdminOverrideStatus.REJECTED
        override.metadata = {
            **(override.metadata or {}),
            "rejected_by_id": getattr(rejected_by, "id", None),
            "rejection_reason": reason.strip(),
        }
        override.save(
            update_fields=[
                "status",
                "metadata",
                "updated_at",
            ]
        )

        return override

    @classmethod
    @transaction.atomic
    def apply_override(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        applied_by,
        idempotency_key: str | None = None,
    ) -> SpecialOrderAdminOverride:
        """
        Apply an approved override.
        """
        cls._validate_admin(actor=applied_by)

        override = cls._lock_override(override=override)

        if override.status != AdminOverrideStatus.APPROVED:
            raise ValueError("Only approved overrides can be applied.")

        if override.override_type == AdminOverrideType.MANUAL_FUNDING_ADJUSTMENT:
            cls._apply_manual_funding_adjustment(
                override=override,
                applied_by=applied_by,
                idempotency_key=idempotency_key,
            )
        elif override.override_type == AdminOverrideType.FORCE_UNLOCK_DELIVERY:
            cls._apply_force_unlock_delivery(
                override=override,
                applied_by=applied_by,
            )
        elif override.override_type == AdminOverrideType.FORCE_COMPLETE:
            cls._apply_force_complete(
                override=override,
                applied_by=applied_by,
            )
        elif override.override_type == AdminOverrideType.FORCE_MARK_FUNDED:
            cls._apply_force_mark_funded(
                override=override,
                applied_by=applied_by,
                idempotency_key=idempotency_key,
            )
        elif override.override_type == AdminOverrideType.WAIVE_MILESTONE:
            raise NotImplementedError(
                "Waive milestone should be implemented with a milestone id."
            )
        else:
            raise ValueError("Unsupported override type.")

        override.status = AdminOverrideStatus.APPLIED
        override.applied_by = applied_by
        override.applied_at = timezone.now()
        override.save(
            update_fields=[
                "status",
                "applied_by",
                "applied_at",
                "payment_application_id",
                "delivery_checkpoint",
                "ledger_entry_reference",
                "updated_at",
            ]
        )

        return override

    @classmethod
    def _apply_manual_funding_adjustment(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        applied_by,
        idempotency_key: str | None,
    ) -> None:
        """
        Apply an admin funding adjustment as a payment application.
        """
        if override.amount is None or override.amount <= Decimal("0.00"):
            raise ValueError("Manual funding adjustment requires amount.")

        payment_application = SpecialOrderPaymentApplicationService.apply_payment(
            special_order=override.special_order,
            amount=override.amount,
            source=PaymentApplicationSource.ADMIN_ADJUSTMENT,
            idempotency_key=(
                idempotency_key
                or f"admin_override:{override.id}:funding_adjustment"
            ),
            ledger_entry_reference=override.ledger_entry_reference,
            applied_by=applied_by,
            metadata={
                "admin_override_id": override.id,
                "reason": override.reason,
            },
        )

        override.payment_application_id = payment_application.id

    @classmethod
    def _apply_force_mark_funded(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        applied_by,
        idempotency_key: str | None,
    ) -> None:
        """
        Force mark remaining balance as funded through admin adjustment.
        """
        funding_plan = override.special_order.funding_plan
        remaining_balance = funding_plan.balance_amount

        if remaining_balance <= Decimal("0.00"):
            return

        payment_application = SpecialOrderPaymentApplicationService.apply_payment(
            special_order=override.special_order,
            amount=remaining_balance,
            source=PaymentApplicationSource.ADMIN_ADJUSTMENT,
            idempotency_key=(
                idempotency_key
                or f"admin_override:{override.id}:force_mark_funded"
            ),
            ledger_entry_reference=override.ledger_entry_reference,
            applied_by=applied_by,
            metadata={
                "admin_override_id": override.id,
                "reason": override.reason,
                "force_mark_funded": True,
            },
        )

        override.payment_application_id = payment_application.id

    @classmethod
    def _apply_force_unlock_delivery(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        applied_by,
    ) -> None:
        """
        Waive or unlock delivery checkpoint.
        """
        checkpoint = override.delivery_checkpoint

        if checkpoint is None:
            raise ValueError(
                "Force unlock delivery requires delivery checkpoint."
            )

        checkpoint.status = DeliveryCheckpointStatus.WAIVED
        checkpoint.unlocked_at = timezone.now()
        checkpoint.unlocked_by = applied_by
        checkpoint.waiver_reason = override.reason
        checkpoint.save(
            update_fields=[
                "status",
                "unlocked_at",
                "unlocked_by",
                "waiver_reason",
                "updated_at",
            ]
        )

    @classmethod
    def _apply_force_complete(
        cls,
        *,
        override: SpecialOrderAdminOverride,
        applied_by,
    ) -> None:
        """
        Force complete the special order.
        """
        SpecialOrderStateService.transition(
            special_order=override.special_order,
            to_status=SpecialOrderStatus.COMPLETED,
            changed_by=applied_by,
            reason=override.reason,
            metadata={
                "admin_override_id": override.id,
                "override_type": override.override_type,
            },
        )

    @staticmethod
    def _lock_override(
        *,
        override: SpecialOrderAdminOverride,
    ) -> SpecialOrderAdminOverride:
        """
        Lock override row.
        """
        return SpecialOrderAdminOverride.objects.select_for_update().get(
            id=override.id,
            website=override.website,
        )

    @classmethod
    def _validate_admin(cls, *, actor) -> None:
        """
        Ensure actor is admin or superadmin.
        """
        role = str(getattr(actor, "role", "")).lower()

        if role not in cls.ADMIN_ROLES:
            raise PermissionError("Admin override requires admin access.")

    @staticmethod
    def _validate_override_type(*, override_type: str) -> None:
        """
        Validate override type.
        """
        valid_types = {
            AdminOverrideType.FORCE_MARK_FUNDED,
            AdminOverrideType.FORCE_UNLOCK_DELIVERY,
            AdminOverrideType.FORCE_COMPLETE,
            AdminOverrideType.MANUAL_PRICE_ADJUSTMENT,
            AdminOverrideType.MANUAL_FUNDING_ADJUSTMENT,
            AdminOverrideType.CANCEL_FUNDING_PLAN,
            AdminOverrideType.WAIVE_MILESTONE,
        }

        if override_type not in valid_types:
            raise ValueError("Invalid admin override type.")