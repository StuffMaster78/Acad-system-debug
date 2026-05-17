"""
Computes writer earnings for a completed order.

THE CARDINAL RULE
-----------------
This service reads from RateCardSnapshot ONLY.
It never reads from WriterLevelSettings directly.
It never reads from WriterLevel directly.
It never reads from WriterProfile.writer_level directly.

If the snapshot does not exist, raise RateCardSnapshotMissingError.
Do not fall back to live settings — that would produce wrong numbers
for any order assigned before a rate change.

INPUTS
------
    snapshot: RateCardSnapshot — frozen rates at assignment time
    order:    orders.Order     — pages, slides, deadline, urgency

OUTPUT
------
    EarningsResult — a dataclass, not a model.
    Saved to WriterPayment by writer_compensation.services.payment_service.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from writer_management.exceptions import RateCardSnapshotMissingError

logger = logging.getLogger(__name__)

CENTS = Decimal("0.01")


@dataclass(frozen=True)
class EarningsResult:
    """
    Immutable result of an earnings calculation.

    All amounts in the order's currency.
    tip_writer_share is computed separately when a tip arrives —
    not at order completion time.
    """
    base_earnings:     Decimal   # pages/slides/charts at base rate
    urgency_uplift:    Decimal   # additional pay for urgency
    gross_earnings:    Decimal   # base + urgency
    tip_percentage:    Decimal   # writer's tip retention rate (for tips app)
    level_name:        str       # which level was applied
    earning_mode:      str       # how earnings were computed
    is_urgent:         bool
    calculation_notes: list[str] # audit trail of what was applied


class EarningsCalculator:

    @staticmethod
    def calculate(snapshot, order) -> EarningsResult:
        """
        Calculate writer earnings for a completed order.

        Args:
            snapshot: RateCardSnapshot for this order.
            order:    orders.Order with pages, slides, deadline resolved.

        Returns:
            EarningsResult — call payment_service.record() to persist.

        Raises:
            RateCardSnapshotMissingError if snapshot is None.
            ValueError if order has no resolvable page/slide count.
        """
        if snapshot is None:
            raise RateCardSnapshotMissingError(
                f"Order {getattr(order, 'pk', '?')} has no RateCardSnapshot. "
                "Earnings cannot be calculated. "
                "Ensure RateCardSnapshotService.capture() was called at assignment."
            )

        notes = []
        mode = snapshot.earning_mode

        # --- Base earnings ---
        if mode == "fixed_per_page":
            base = EarningsCalculator._fixed_base(snapshot, order, notes)
        elif mode == "percentage_of_order_cost":
            base = EarningsCalculator._pct_of_cost(snapshot, order, notes)
        elif mode == "percentage_of_order_total":
            base = EarningsCalculator._pct_of_total(snapshot, order, notes)
        else:
            logger.warning(
                "Unknown earning_mode '%s' on snapshot %s — "
                "falling back to fixed_per_page.",
                mode,
                snapshot.pk,
            )
            base = EarningsCalculator._fixed_base(snapshot, order, notes)
            notes.append(f"WARNING: unknown mode '{mode}', used fixed_per_page fallback")

        # --- Urgency uplift ---
        is_urgent = EarningsCalculator._is_urgent(snapshot, order)
        urgency_uplift = Decimal("0.00")

        if is_urgent:
            uplift_from_surcharge = (
                EarningsCalculator._page_count(order)
                * snapshot.urgent_order_surcharge
            )
            uplift_from_multiplier = base * (snapshot.urgent_multiplier - Decimal("1.00"))
            urgency_uplift = (
                uplift_from_surcharge + uplift_from_multiplier
            ).quantize(CENTS, rounding=ROUND_HALF_UP)
            notes.append(
                f"Urgency: surcharge={uplift_from_surcharge} "
                f"multiplier_uplift={uplift_from_multiplier}"
            )

        gross = (base + urgency_uplift).quantize(CENTS, rounding=ROUND_HALF_UP)

        logger.info(
            "EarningsCalculator: order=%s writer=%s level=%s "
            "mode=%s base=%s urgency=%s gross=%s",
            order.pk,
            snapshot.writer_id,
            snapshot.level_name,
            mode,
            base,
            urgency_uplift,
            gross,
        )

        return EarningsResult(
            base_earnings=base,
            urgency_uplift=urgency_uplift,
            gross_earnings=gross,
            tip_percentage=snapshot.tip_percentage,
            level_name=snapshot.level_name,
            earning_mode=mode,
            is_urgent=is_urgent,
            calculation_notes=notes,
        )

    # ----------------------------------------------------------------
    # EARNING MODE IMPLEMENTATIONS
    # ----------------------------------------------------------------

    @staticmethod
    def _fixed_base(snapshot, order, notes: list) -> Decimal:
        pages  = EarningsCalculator._page_count(order)
        slides = EarningsCalculator._slide_count(order)
        charts = EarningsCalculator._chart_count(order)

        page_pay  = pages  * snapshot.base_pay_per_page
        slide_pay = slides * snapshot.base_pay_per_slide
        chart_pay = charts * snapshot.base_pay_per_chart

        notes.append(
            f"Fixed: {pages}p x {snapshot.base_pay_per_page} "
            f"+ {slides}s x {snapshot.base_pay_per_slide} "
            f"+ {charts}c x {snapshot.base_pay_per_chart}"
        )
        return (page_pay + slide_pay + chart_pay).quantize(
            CENTS, rounding=ROUND_HALF_UP
        )

    @staticmethod
    def _pct_of_cost(snapshot, order, notes: list) -> Decimal:
        """Percentage of order cost before discounts."""
        cost = EarningsCalculator._order_cost(order)
        # WriterLevelSettings stores this as a percentage integer
        # e.g. 70.00 means 70%
        pct = snapshot.base_pay_per_page  # reused field — see note below
        # NOTE: in percentage modes, base_pay_per_page stores the
        # percentage value (e.g. Decimal("70.00") = 70%).
        # This is a known naming awkwardness — a future migration
        # should add explicit pct_of_cost and pct_of_total fields
        # to RateCardSnapshot. For now, document here.
        result = (cost * pct / Decimal("100")).quantize(
            CENTS, rounding=ROUND_HALF_UP
        )
        notes.append(f"PctOfCost: {pct}% of cost={cost}")
        return result

    @staticmethod
    def _pct_of_total(snapshot, order, notes: list) -> Decimal:
        """Percentage of order total after discounts."""
        total = EarningsCalculator._order_total(order)
        pct = snapshot.base_pay_per_slide  # see note above
        result = (total * pct / Decimal("100")).quantize(
            CENTS, rounding=ROUND_HALF_UP
        )
        notes.append(f"PctOfTotal: {pct}% of total={total}")
        return result

    # ----------------------------------------------------------------
    # ORDER FIELD ACCESSORS
    # Centralised so we only need to update one place if Order changes.
    # ----------------------------------------------------------------

    @staticmethod
    def _page_count(order) -> Decimal:
        return Decimal(str(getattr(order, "number_of_pages", 0) or 0))

    @staticmethod
    def _slide_count(order) -> Decimal:
        return Decimal(str(getattr(order, "number_of_slides", 0) or 0))

    @staticmethod
    def _chart_count(order) -> Decimal:
        return Decimal(str(getattr(order, "number_of_charts", 0) or 0))

    @staticmethod
    def _order_cost(order) -> Decimal:
        """Order cost before discounts."""
        return Decimal(str(getattr(order, "cost", None) or
                           getattr(order, "total_price", 0) or 0))

    @staticmethod
    def _order_total(order) -> Decimal:
        """Order total after discounts."""
        return Decimal(str(getattr(order, "discounted_amount", None) or
                           getattr(order, "total_price", 0) or 0))

    @staticmethod
    def _is_urgent(snapshot, order) -> bool:
        """
        Determine if the order qualifies as urgent based on the
        threshold that was configured when the order was assigned.
        """
        deadline = getattr(order, "writer_deadline", None) or \
                   getattr(order, "deadline", None)
        assigned_at = getattr(order, "assigned_at", None)

        if deadline is None or assigned_at is None:
            return False

        hours_available = (deadline - assigned_at).total_seconds() / 3600
        return hours_available <= snapshot.urgent_time_threshold_hours