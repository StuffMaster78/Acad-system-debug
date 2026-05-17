from __future__ import annotations

import logging
from datetime import timedelta 
from decimal import Decimal

from django.utils.timezone import now

from writer_compensation.enums.compensation_enums import EventStatus, EventType
from writer_compensation.services.event_intake_service import EventIntakeService

logger = logging.getLogger(__name__)


class BonusService:
    """
    Calculate and apply bonuses to writer compensation.

    All bonus CompensationEvents are created via EventIntakeService.record()
    — never directly via CompensationEvent.objects.create().
    """

    PERFORMANCE_BONUS_RATES = {
        (Decimal("4.8"), Decimal("0.98")): Decimal("0.15"),
        (Decimal("4.5"), Decimal("0.95")): Decimal("0.10"),
        (Decimal("4.0"), Decimal("0.90")): Decimal("0.05"),
    }

    MILESTONE_BONUSES = [
        (10,  Decimal("50.00")),
        (50,  Decimal("150.00")),
        (100, Decimal("300.00")),
        (250, Decimal("750.00")),
        (500, Decimal("1500.00")),
    ]

    @staticmethod
    def calculate_for_order(writer, order, base_amount: Decimal) -> Decimal:
        """
        Calculate performance bonus for a completed order.
        Returns bonus amount or Decimal("0.00") if not qualified.
        Pure calculation — does not create any events.
        """
        from writer_management.models.writer_performance import WriterPerformance

        try:
            perf = WriterPerformance.objects.get(writer=writer)
        except WriterPerformance.DoesNotExist:
            logger.warning("WriterPerformance missing for writer %s", writer.pk)
            return Decimal("0.00")

        completion_rate = (
            Decimal(str(perf.completed_orders / perf.total_orders))
            if perf.total_orders > 0 else Decimal("0")
        )

        bonus_rate = Decimal("0.00")
        for (min_rating, min_completion), rate in BonusService.PERFORMANCE_BONUS_RATES.items():
            if perf.average_rating >= min_rating and completion_rate >= min_completion:
                bonus_rate = rate
                break

        if bonus_rate > 0:
            bonus = (base_amount * bonus_rate).quantize(Decimal("0.01"))
            logger.info(
                "Performance bonus for writer %s: $%s (%s%%) on order %s",
                writer.pk, bonus, bonus_rate * 100, order.pk,
            )
            return bonus

        return Decimal("0.00")

    @staticmethod
    def check_milestone_bonuses(writer) -> list:
        """
        Check which milestone bonuses the writer has newly qualified for.
        Returns list of dicts — does not create events.
        """
        from writer_management.models.writer_performance import WriterPerformance
        from writer_compensation.models.writer_bonus import MilestoneBonus

        try:
            perf = WriterPerformance.objects.get(writer=writer)
        except WriterPerformance.DoesNotExist:
            return []

        completed  = perf.completed_orders
        new_bonuses = []

        for threshold, amount in BonusService.MILESTONE_BONUSES:
            if completed >= threshold:
                already_awarded = MilestoneBonus.objects.filter(
                    writer=writer,
                    milestone=threshold,
                ).exists()

                if not already_awarded:
                    new_bonuses.append({
                        "milestone":    threshold,
                        "bonus_amount": amount,
                        "reason":       f"Milestone: {threshold} orders completed",
                    })
                    logger.info(
                        "Milestone bonus qualified: writer %s, %s orders, $%s",
                        writer.pk, threshold, amount,
                    )

        return new_bonuses

    @staticmethod
    def apply_milestone_bonus(
        writer,
        milestone: int,
        amount: Decimal,
        website=None,
        created_by=None,
    ):
        """
        Record and apply a milestone bonus.
        Returns CompensationEvent or None if already awarded.
        """
        from writer_compensation.models.writer_bonus import MilestoneBonus

        milestone_record, created = MilestoneBonus.objects.get_or_create(
            writer=writer,
            milestone=milestone,
            defaults={"amount": amount, "awarded_at": now()},
        )

        if not created:
            return None

        resolved_website = website or getattr(writer, "website", None)
        if resolved_website is None:
            logger.error(
                "Cannot apply milestone bonus — no website for writer %s",
                writer.pk,
            )
            return None

        # Stable idempotency key — milestone per writer is unique,
        # no timestamp so retries are safe.
        idempotency_key = f"milestone-{writer.pk}-{milestone}"

        event, _ = EventIntakeService.record(
            website=resolved_website,
            writer=writer,
            event_type=EventType.MILESTONE_BONUS,          # FIX: enum not raw string
            amount=amount,
            title=f"Milestone bonus — {milestone} orders",
            notes=f"Milestone bonus: {milestone} orders completed",
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        logger.info(
            "Applied milestone bonus: writer %s, milestone %s, event %s",
            writer.pk, milestone, event.pk,
        )
        return event

    @staticmethod
    def apply_performance_bonus(
        writer,
        order,
        base_amount: Decimal,
        website=None,
        created_by=None,
    ):
        """
        Calculate and apply a performance bonus for a completed order.
        Returns CompensationEvent or None if no bonus qualifies.
        """
        bonus_amount = BonusService.calculate_for_order(writer, order, base_amount)
        if bonus_amount == Decimal("0.00"):
            return None

        resolved_website = website or getattr(writer, "website", None)
        if resolved_website is None:
            logger.error(
                "Cannot apply performance bonus — no website for writer %s",
                writer.pk,
            )
            return None

        idempotency_key = f"perf-bonus-{writer.pk}-{order.pk}"

        event, _ = EventIntakeService.record(
            website=resolved_website,
            writer=writer,
            event_type=EventType.PERFORMANCE_BONUS,       # FIX: enum value
            amount=bonus_amount,
            source_type="order",
            source_id=order.pk,
            title=f"Performance bonus — Order #{order.pk}",
            notes=f"Performance bonus on order {order.pk}",
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        return event

    @staticmethod
    def apply_retention_bonus(
        writer,
        period_days: int = 30,
        website=None,
        created_by=None,
    ):
        """
        Calculate and apply retention bonus.

        FIX: timedelta imported from datetime not django.utils.timezone.
        """
        from writer_management.models import WriterPerformance

        try:
            perf = WriterPerformance.objects.get(writer=writer)
        except WriterPerformance.DoesNotExist:
            return None

        completion_rate = (
            Decimal(str(perf.completed_orders / perf.total_orders))
            if perf.total_orders > 0 else Decimal("0")
        )

        if not (
            perf.average_rating >= Decimal("4.0")
            and completion_rate >= Decimal("0.80")
            and perf.cancelled_orders == 0
        ):
            return None

        if perf.average_rating >= Decimal("4.8"):
            bonus = Decimal("25.00")
        elif perf.average_rating >= Decimal("4.5"):
            bonus = Decimal("15.00")
        else:
            bonus = Decimal("5.00")

        resolved_website = website or getattr(writer, "website", None)
        if resolved_website is None:
            return None

        period_label = now().strftime("%Y-%m")
        idempotency_key = f"retention-{writer.pk}-{period_label}"

        event, _ = EventIntakeService.record(
            website=resolved_website,
            writer=writer,
            event_type=EventType.RETENTION_BONUS,         # FIX: enum value
            amount=bonus,
            title=f"Retention bonus — {period_label}",
            notes=(
                f"Retention bonus: rating={perf.average_rating}, "
                f"completion={completion_rate * 100:.0f}%"
            ),
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        logger.info(
            "Retention bonus: writer %s $%s rating=%s",
            writer.pk, bonus, perf.average_rating,
        )
        return event

    @staticmethod
    def sync_referral_bonuses(
        writer,
        period_start,
        period_end,
        website=None,
        created_by=None,
    ) -> list:
        """
        Calculate and apply referral bonuses earned during period.
        Returns list of created CompensationEvents.
        """
        from writer_compensation.models.writer_bonus import ReferralBonus
        from orders.models.orders import Order

        try:
            referrals = writer.referred_writers.all()
        except AttributeError:
            logger.warning("No referral tracking for writer %s", writer.pk)
            return []

        resolved_website = website or getattr(writer, "website", None)
        if resolved_website is None:
            return []

        created_events = []

        for referred_writer in referrals:
            completed_orders = Order.objects.filter(
                assigned_writer=referred_writer.user,
                status="completed",
                completed_at__date__gte=period_start,
                completed_at__date__lte=period_end,
            ).count()

            existing = ReferralBonus.objects.filter(
                referrer=writer,
                referred_writer=referred_writer,
                period_start=period_start,
                period_end=period_end,
            ).count()

            new_orders = max(0, completed_orders - existing)
            if new_orders == 0:
                continue

            amount = Decimal(str(new_orders * 10))
            idempotency_key = (
                f"referral-{writer.pk}-{referred_writer.pk}"
                f"-{period_start}-{period_end}"
            )

            event, _ = EventIntakeService.record(
                website=resolved_website,
                writer=writer,
                event_type=EventType.REFERRAL_BONUS,      # FIX: enum value
                amount=amount,
                source_type="writer_referral",
                source_id=referred_writer.pk,
                title=f"Referral bonus — {new_orders} orders",
                notes=(
                    f"Referral: {new_orders} orders by "
                    f"{referred_writer.user.username}"
                ),
                idempotency_key=idempotency_key,
                created_by=created_by,
            )

            ReferralBonus.objects.get_or_create(
                referrer=writer,
                referred_writer=referred_writer,
                period_start=period_start,
                period_end=period_end,
                defaults={"amount": amount, "compensation_event": event},
            )

            created_events.append(event)
            logger.info(
                "Referral bonus: writer %s referred %s, %s orders, $%s",
                writer.pk, referred_writer.pk, new_orders, amount,
            )

        return created_events

    @staticmethod
    def get_bonus_history(writer, limit: int = 50) -> list:
        """
        Bonus event history for a writer.

        FIX: uses EventType enum values not raw strings.
        """
        from writer_compensation.models.compensation_event import CompensationEvent

        return list(
            CompensationEvent.objects.filter(
                writer=writer,
                event_type__in=[
                    EventType.PERFORMANCE_BONUS,   # FIX: enum values
                    EventType.MILESTONE_BONUS,
                    EventType.REFERRAL_BONUS,
                    EventType.RETENTION_BONUS,
                    EventType.BONUS,
                ],
            ).order_by("-created_at")[:limit]
        )