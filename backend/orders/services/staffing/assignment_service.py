"""
order_actions/services/assignment_service.py

Assigns a writer to an order.

This is the orchestration layer. It coordinates across three apps:
    writer_management   — eligibility check, capacity update
    writer_compensation — rate card snapshot capture
    orders              — order status update

THE FULL FLOW
-------------

    Client or admin triggers assignment
            │
            ▼
    AssignmentService.assign(order, writer_profile)
            │
            ├─ 1. Eligibility check
            │       WriterEligibilityService.is_eligible(writer_profile)
            │       Raises WriterNotEligibleError if any gate fails.
            │
            ├─ 2. Capture rate card snapshot  ◄─── KEY STEP
            │       RateCardSnapshotService.capture(writer_profile, order)
            │       Freezes WriterLevelSettings values into RateCardSnapshot.
            │       If this fails → entire transaction rolls back.
            │       No snapshot = no assignment.
            │
            ├─ 3. Update order
            │       order.assigned_writer = writer_profile
            │       order.assigned_at = now()
            │       order.status = "assigned"
            │       order.save(update_fields=[...])
            │
            ├─ 4. Increment writer capacity counter
            │       WriterCapacity.objects.filter(writer=writer_profile)
            │           .update(active_orders_count=F("active_orders_count") + 1)
            │       F() expression — no race condition.
            │
            └─ 5. Emit assignment event
                    (notification system, outbox, or signal)


EARNINGS FLOW (at order completion — separate service)
------------------------------------------------------

    Order marked complete
            │
            ▼
    PaymentService.compute_and_record(order)
            │
            ├─ 1. Fetch snapshot
            │       snapshot = RateCardSnapshotService.get_for_order(order)
            │       Raises RateCardSnapshot.DoesNotExist if missing.
            │
            ├─ 2. Calculate earnings
            │       result = EarningsCalculator.calculate(snapshot, order)
            │       Returns EarningsResult dataclass.
            │
            ├─ 3. Record payment
            │       WriterPayment.objects.create(
            │           writer=snapshot.writer,
            │           order=order,
            │           gross_amount=result.gross_earnings,
            │           tip_percentage=result.tip_percentage,
            │           level_name=result.level_name,
            │           calculation_notes=result.calculation_notes,
            │       )
            │
            └─ 4. Decrement writer capacity counter
                    WriterCapacity.objects.filter(writer=snapshot.writer)
                        .update(active_orders_count=F("active_orders_count") - 1)


TIP FLOW (when client sends a tip — tips app)
---------------------------------------------

    TipCreationService.create_tip(client, receiver_user, order, tip_amount)
            │
            ├─ 1. Resolve writer profile
            │       profile = receiver_user.account_profile.writer_profile
            │
            ├─ 2. Get rate card snapshot for this order
            │       snapshot = RateCardSnapshotService.get_for_order(order)
            │       tip_percentage = snapshot.tip_percentage
            │
            ├─ 3. Compute split
            │       writer_share = tip_amount * tip_percentage / 100
            │       platform_fee = tip_amount - writer_share
            │
            └─ 4. Create Tip record
                    Tip.objects.create(
                        receiver=receiver_user,
                        order=order,
                        gross_amount=tip_amount,
                        writer_share=writer_share,
                        platform_fee=platform_fee,
                        tip_percentage_applied=tip_percentage,
                        ...
                    )

    NOTE: The tips app reads tip_percentage from RateCardSnapshot,
    NOT from WriterLevelSettings. This ensures a writer's tip split
    is always the rate that applied when the order was assigned,
    not their current rate.
"""

import logging

from django.db import transaction
from django.db.models import F
from django.utils.timezone import now

from writer_management.services.assignment_eligibility_service import (
    WriterEligibilityService,
)
from writer_management.exceptions import WriterNotEligibleError
from writer_compensation.services.rate_card_snapshot_service import (
    RateCardSnapshotService,
)
from writer_management.models.writer_capacity import WriterCapacity

logger = logging.getLogger(__name__)


class AssignmentService:

    @staticmethod
    @transaction.atomic
    def assign(order, writer_profile) -> None:
        """
        Assign a writer to an order atomically.

        All steps run in one transaction. Any failure rolls back
        everything — the order stays unassigned, the snapshot is
        not created, the counter is not incremented.

        Args:
            order:          orders.Order — must be in assignable status.
            writer_profile: writer_management.WriterProfile.

        Raises:
            WriterNotEligibleError  — writer fails eligibility check.
            LevelSettingsMissingError — writer has no level or settings.
            AlreadyAssignedError    — order already has an assignment.
        """
        logger.info(
            "AssignmentService.assign: order=%s writer=%s",
            order.pk,
            writer_profile.registration_id,
        )

        # ── Step 1: Eligibility ──────────────────────────────────────
        if not WriterEligibilityService.is_eligible(writer_profile):
            explanation = WriterEligibilityService.explain(writer_profile)
            raise WriterNotEligibleError(
                f"Writer {writer_profile.registration_id} is not eligible "
                f"for assignment. Reasons: {explanation['reasons']}"
            )

        # ── Step 2: Capture rate card snapshot ───────────────────────
        # This MUST happen before the order is updated.
        # If snapshot capture fails (no level, no settings),
        # the transaction rolls back and the order is untouched.
        snapshot = RateCardSnapshotService.capture(writer_profile, order)

        # ── Step 3: Update order ─────────────────────────────────────
        order.assigned_writer = writer_profile
        order.assigned_at = now()
        order.status = "assigned"
        order.save(update_fields=["assigned_writer", "assigned_at", "status"])

        # ── Step 4: Increment capacity counter ───────────────────────
        # F() expression — atomic increment, no read-modify-write race.
        updated = WriterCapacity.objects.filter(
            writer=writer_profile,
        ).update(
            active_orders_count=F("active_orders_count") + 1
        )

        if updated == 0:
            logger.error(
                "WriterCapacity row missing for writer %s — "
                "counter not incremented.",
                writer_profile.registration_id,
            )
            # Do not raise — assignment proceeds, but alert is needed.
            # A missing capacity row is a data integrity issue to fix
            # separately (management command: reconcile_writer_capacity).

        logger.info(
            "Assignment complete: order=%s writer=%s snapshot=%s",
            order.pk,
            writer_profile.registration_id,
            snapshot.pk,
        )

    @staticmethod
    @transaction.atomic
    def unassign(order, reason: str = "") -> None:
        """
        Remove a writer from an order and decrement their counter.

        Does NOT delete the RateCardSnapshot — it is a permanent
        financial audit record even if the assignment was reversed.

        Args:
            order:  orders.Order with assigned_writer set.
            reason: Optional reason string for audit log.
        """
        writer_profile = order.assigned_writer
        if writer_profile is None:
            logger.warning(
                "unassign called on order %s with no assigned writer.",
                order.pk,
            )
            return

        order.assigned_writer = None
        order.assigned_at = None
        order.status = "unassigned"
        order.save(update_fields=["assigned_writer", "assigned_at", "status"])

        WriterCapacity.objects.filter(
            writer=writer_profile,
        ).update(
            active_orders_count=F("active_orders_count") - 1
        )

        logger.info(
            "Unassignment complete: order=%s writer=%s reason=%s",
            order.pk,
            writer_profile.registration_id,
            reason,
        )