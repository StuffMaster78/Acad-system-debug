from __future__ import annotations

from special_orders.constants import (
    DeliveryCheckpointStatus,
    DeliveryCheckpointType,
    FundingMilestoneStatus,
    FundingPlanStatus,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderDeliveryCheckpoint,
    SpecialOrderFundingMilestone,
)


class SpecialOrderDeliveryGuardService:
    """
    Enforce funding gates before staffing, drafts, delivery, and completion.
    """

    @staticmethod
    def can_start_work(*, special_order: SpecialOrder) -> bool:
        """
        Return true if required staffing milestones are paid.
        """
        blocking_milestones = SpecialOrderFundingMilestone.objects.filter(
            website=special_order.website,
            special_order=special_order,
            required_before_staffing=True,
        ).exclude(status=FundingMilestoneStatus.PAID)

        return not blocking_milestones.exists()

    @staticmethod
    def can_deliver_final(*, special_order: SpecialOrder) -> bool:
        """
        Return true if final delivery is financially unlocked.
        """
        funding_plan = getattr(special_order, "funding_plan", None)

        if funding_plan is not None:
            if funding_plan.requires_full_payment_before_delivery:
                return funding_plan.status == FundingPlanStatus.FUNDED

        blocking_milestones = SpecialOrderFundingMilestone.objects.filter(
            website=special_order.website,
            special_order=special_order,
            required_before_delivery=True,
        ).exclude(status=FundingMilestoneStatus.PAID)

        return not blocking_milestones.exists()

    @classmethod
    def assert_can_start_work(
        cls,
        *,
        special_order: SpecialOrder,
    ) -> None:
        """
        Raise if staffing/start-work gate is blocked.
        """
        if not cls.can_start_work(special_order=special_order):
            raise ValueError(
                "Special order cannot start before required funding is paid."
            )

    @classmethod
    def assert_can_deliver_final(
        cls,
        *,
        special_order: SpecialOrder,
    ) -> None:
        """
        Raise if final delivery gate is blocked.
        """
        if not cls.can_deliver_final(special_order=special_order):
            raise ValueError(
                "Final delivery is blocked until required payment is complete."
            )

    @classmethod
    def sync_delivery_checkpoint(
        cls,
        *,
        special_order: SpecialOrder,
        checkpoint_type: str,
        required_milestone: SpecialOrderFundingMilestone | None = None,
    ) -> SpecialOrderDeliveryCheckpoint:
        """
        Create or update a delivery checkpoint based on current funding state.
        """
        is_unlocked = True

        if checkpoint_type == DeliveryCheckpointType.BEFORE_STAFFING:
            is_unlocked = cls.can_start_work(special_order=special_order)

        if checkpoint_type == DeliveryCheckpointType.BEFORE_FINAL_DELIVERY:
            is_unlocked = cls.can_deliver_final(special_order=special_order)

        checkpoint, _created = (
            SpecialOrderDeliveryCheckpoint.objects.update_or_create(
                website=special_order.website,
                special_order=special_order,
                checkpoint_type=checkpoint_type,
                defaults={
                    "required_milestone": required_milestone,
                    "status": (
                        DeliveryCheckpointStatus.UNLOCKED
                        if is_unlocked
                        else DeliveryCheckpointStatus.BLOCKED
                    ),
                },
            )
        )

        return checkpoint