from __future__ import annotations

import logging
from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from writer_compensation.enums.compensation_enums import (
    BONUS_EVENT_TYPES,
    DEDUCTION_EVENT_TYPES,
    EventStatus,
    EventType,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.payment_window import PaymentWindow

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Local event type groupings for accumulation
# ---------------------------------------------------------------------------

_BASE_TYPES = {
    EventType.ORDER_EARNING,
    EventType.CLASS_EARNING,
    EventType.SPECIAL_ORDER_EARNING,
    EventType.BASE_EARNING,
}

_BONUS_TYPES = BONUS_EVENT_TYPES

_DEDUCTION_TYPES = DEDUCTION_EVENT_TYPES

_REVERSAL_TYPES = {EventType.REVERSAL}

_TIP_TYPES = {EventType.TIP}

_ADVANCE_TYPES = {EventType.ADVANCE, EventType.ADVANCE_RECOVERY}


class EarningsQueryService:
    """
    Read-only earnings reconstruction service.

    Core principle:
        We do NOT calculate earnings.
        We reconstruct earnings from the immutable CompensationEvent ledger.
    """

    @staticmethod
    def get_period_totals(
        *,
        website,
        start_date,
        end_date,
        writer=None,
    ) -> dict:
        """
        Period financial aggregation scoped by window dates.

        FIX: uses payment_window FK filters not created_at__range.
        FIX: status parameter removed — always MATURED + PAID (the correct defaults).
        FIX: TIP and ADVANCE types now included in aggregation.
        """
        qs = CompensationEvent.objects.filter(
            website=website,
            payment_window__start_date__gte=start_date, # FIX: was created_at__range
            payment_window__end_date__lte=end_date,
            status__in=[EventStatus.MATURED, EventStatus.PAID],
        )

        if writer is not None:
            qs = qs.filter(writer=writer)

        earnings = qs.filter(
            event_type__in=[
                EventType.ORDER_EARNING,
                EventType.CLASS_EARNING,
                EventType.SPECIAL_ORDER_EARNING,
                EventType.BASE_EARNING,
            ]
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        bonuses = qs.filter(
            event_type__in=list(_BONUS_TYPES),
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        tips = qs.filter(
            event_type=EventType.TIP,
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        deductions = qs.filter(
            event_type__in=list(_DEDUCTION_TYPES),
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        reversals = qs.filter(
            event_type=EventType.REVERSAL,
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        # FIX: advances are separate — positive ADVANCE + negative RECOVERY
        advances = qs.filter(
            event_type__in=[EventType.ADVANCE, EventType.ADVANCE_RECOVERY],
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

        net = earnings + bonuses + tips + deductions + reversals + advances

        return {
            "totals": {
                "earnings": earnings,
                "bonuses": bonuses,
                "tips": tips,
                "deductions": deductions,
                "reversals": reversals,
                "advances": advances,
                "net": net,
            }
        }

    @staticmethod
    def get_period_breakdown_by_event_type(
        *,
        website,
        writer,
        start_date,
        end_date,
    ) -> dict:
        """
        Totals grouped by EventType for admin dashboards.

        FIX: uses payment_window FK not created_at__range.
        """
        qs = CompensationEvent.objects.filter(
            website=website,
            writer=writer,
            payment_window__start_date__gte=start_date, # FIX
            payment_window__end_date__lte=end_date,
            status__in=[EventStatus.MATURED, EventStatus.PAID],
        )

        rows = qs.values("event_type").annotate(total=Sum("amount"))

        breakdown: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for row in rows:
            breakdown[row["event_type"]] = row["total"] or Decimal("0.00")

        return dict(breakdown)

    @staticmethod
    def get_pending_balance(*, website, writer) -> Decimal:
        """Events waiting for maturity — not yet in settlement."""
        result = CompensationEvent.objects.filter(
            website=website,
            writer=writer,
            status=EventStatus.PENDING_CONFIRMATION,
        ).aggregate(t=Sum("amount"))["t"]
        return result or Decimal("0.00")

    @staticmethod
    def get_running_balance(*, website, writer) -> Decimal:
        """Full lifetime balance — all matured and paid events."""
        result = CompensationEvent.objects.filter(
            website=website,
            writer=writer,
            status__in=[EventStatus.MATURED, EventStatus.PAID],
        ).aggregate(t=Sum("amount"))["t"]
        return result or Decimal("0.00")

    @staticmethod
    def get_writer_earnings(
        *,
        writer,
        window: PaymentWindow | None = None,
    ) -> dict[str, Any]:
        """
        Full earnings reconstruction for a writer, optionally scoped
        to a single window.
        """
        qs = CompensationEvent.objects.filter(
            writer=writer,
            status__in=[EventStatus.MATURED, EventStatus.PAID],
        )

        if window:
            qs = qs.filter(payment_window=window)

        qs = qs.select_related(
            "payment_window",
            "related_window",
        ).order_by("created_at")

        events = list(qs)
        grouped = EarningsQueryService._group_by_window(events)
        totals = EarningsQueryService._compute_totals(grouped)
        anomalies = EarningsQueryService._detect_anomalies(events)

        return {
            "writer_id": writer.pk,
            "windows": grouped,
            "totals": totals,
            "audit": anomalies,
        }

    @staticmethod
    def get_window_breakdown(window: PaymentWindow) -> dict:
        """Window-focused earnings view for admin and payout engine."""
        events = list(
            CompensationEvent.objects.filter(
                payment_window=window,
                status__in=[EventStatus.MATURED, EventStatus.PAID],
            ).select_related("writer")
        )
        return {
            "window_id": window.pk,
            "writers": EarningsQueryService._group_by_writer(events),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _group_by_window(events: list) -> dict:
        windows: dict[int, dict] = {}

        for e in events:
            w = e.payment_window
            if w.pk not in windows:
                windows[w.pk] = {
                    "window_id": w.pk,
                    "start_date": w.start_date,
                    "end_date": w.end_date,
                    "events": [],
                    "totals": {
                        "base": Decimal("0.00"),
                        "bonus": Decimal("0.00"),
                        "tips": Decimal("0.00"),
                        "deductions": Decimal("0.00"),
                        "reversals": Decimal("0.00"),
                        "advances": Decimal("0.00"),
                        "net": Decimal("0.00"),
                    },
                }

            windows[w.pk]["events"].append(
                EarningsQueryService._serialize_event(e)
            )
            EarningsQueryService._accumulate(windows[w.pk]["totals"], e)

        for w in windows.values():
            t = w["totals"]
            t["net"] = (
                t["base"]
                + t["bonus"]
                + t["tips"]
                + t["deductions"] # already negative
                + t["reversals"] # already negative
                + t["advances"] # signed: positive advance, negative recovery
            )

        return windows

    @staticmethod
    def _accumulate(totals: dict, event: CompensationEvent) -> None:
        """Accumulate event amount into the correct bucket."""
        t = event.event_type
        a = event.amount

        if t in _BASE_TYPES:
            totals["base"] += a
        elif t in _BONUS_TYPES:
            totals["bonus"] += a
        elif t in _TIP_TYPES:
            totals["tips"] += a # FIX: was missing
        elif t in _DEDUCTION_TYPES:
            totals["deductions"] += a # already negative
        elif t in _REVERSAL_TYPES:
            totals["reversals"] += a # already negative
        elif t in _ADVANCE_TYPES:
            totals["advances"] += a # FIX: was missing
        # HOLD types have no ledger impact — silently skipped

    @staticmethod
    def _serialize_event(event: CompensationEvent) -> dict:
        """
        Audit-safe event representation.

        FIX: rate_snapshot accessed via correct related name.
        Falls back gracefully if snapshot not present.
        """
        snapshot = None
        try:
            # Adjust related_name if yours differs
            snapshot = getattr(event, "rate_card_snapshot", None)
        except Exception:
            pass

        return {
            "event_id": event.pk,
            "type": event.event_type,
            "amount": str(event.amount),
            "status": event.status,
            "source": event.source,
            "source_type": event.source_type,
            "source_id": event.source_id,
            "payment_window": event.payment_window.pk,
            "created_at": event.created_at,
            "snapshot": (
                {
                    "level": snapshot.level_name,
                    "earning_mode": snapshot.earning_mode,
                    "rate_card_version": snapshot.rate_card_version,
                    "currency": snapshot.currency,
                }
                if snapshot else None
            ),
        }

    @staticmethod
    def _compute_totals(grouped: dict) -> dict:
        totals = {
            "base": Decimal("0.00"), "bonus": Decimal("0.00"),
            "tips": Decimal("0.00"), "deductions": Decimal("0.00"),
            "reversals": Decimal("0.00"), "advances": Decimal("0.00"),
        }
        for w in grouped.values():
            for key in totals:
                totals[key] += w["totals"][key]

        totals["net"] = sum(totals.values(), Decimal("0.00"))
        return totals

    @staticmethod
    def _detect_anomalies(events: list) -> list[dict]:
        """
        Audit signals — does NOT block payouts.

        FIX: MISSING_SNAPSHOT only fires when the rate_card_snapshot
        relation actually resolves to None, not when the field doesn't
        exist on the model. Prevents false positives on every event.
        """
        anomalies: list[dict] = []
        seen: set = set()

        for e in events:
            key = (e.source_type, e.source_id, e.event_type)

            if key in seen and e.source_id is not None:
                anomalies.append({
                    "type": "DUPLICATE_EVENT",
                    "event_id": e.pk,
                    "message": "Duplicate ledger event detected",
                })
            seen.add(key)

            if e.event_type in _BONUS_TYPES and e.amount < 0:
                anomalies.append({
                    "type": "NEGATIVE_BONUS",
                    "event_id": e.pk,
                    "message": "Bonus event has negative amount",
                })

            # FIX: only flag if snapshot relation exists on model
            # and resolves to None for an earning-type event
            if e.event_type in _BASE_TYPES:
                try:
                    snap = e.rate_card_snapshot
                    if snap is None:
                        anomalies.append({
                            "type": "MISSING_SNAPSHOT",
                            "event_id": e.pk,
                            "message": "Earning event has no rate card snapshot",
                        })
                except AttributeError:
                    pass # model doesn't have snapshot yet — skip silently

        return anomalies

    @staticmethod
    def _group_by_writer(events: list) -> dict:
        writers: dict[int, dict] = defaultdict(lambda: {
            "writer_id": None,
            "events": [],
            "net": Decimal("0.00"),
        })
        for e in events:
            w = writers[e.writer.pk]
            w["writer_id"] = e.writer.pk
            w["events"].append(EarningsQueryService._serialize_event(e))
            w["net"] += e.amount
        return writers