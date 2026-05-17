from __future__ import annotations

from decimal import Decimal

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from writer_compensation.models.reward_rule import RewardRule
from writer_management.models.writer_performance import (
    WriterPerformanceMetrics,
)


class RewardQualificationService:
    """
    Determines whether a writer qualifies for configured rewards.

    IMPORTANT
    ----------
    This service:
        - evaluates eligibility
        - returns matching rules

    This service does NOT:
        - create payouts
        - create compensation events
        - send notifications
        - mutate balances

    Those responsibilities belong elsewhere.

    FLOW
    ----
    reputation snapshot
        +
    weekly/monthly metrics
        +
    active reward rules
        ->
    qualified reward rules
    """

    @classmethod
    def qualified_rules_for_writer(
        cls,
        *,
        reputation_snapshot: WriterReputationSnapshot,
        performance_metrics: WriterPerformanceMetrics | None,
    ) -> list[RewardRule]:
        """
        Return all active reward rules the writer qualifies for.
        """

        rules = RewardRule.objects.filter(
            website=reputation_snapshot.website,
            is_active=True,
        )

        qualified_rules: list[RewardRule] = []

        for rule in rules:
            if cls._qualifies(
                rule=rule,
                reputation_snapshot=reputation_snapshot,
                performance_metrics=performance_metrics,
            ):
                qualified_rules.append(rule)

        return qualified_rules

    @classmethod
    def _qualifies(
        cls,
        *,
        rule: RewardRule,
        reputation_snapshot: WriterReputationSnapshot,
        performance_metrics: WriterPerformanceMetrics | None,
    ) -> bool:
        """
        Evaluate all configured thresholds.
        """

        if (
            rule.minimum_avg_rating is not None
            and reputation_snapshot.rating
            < rule.minimum_avg_rating
        ):
            return False

        if (
            rule.minimum_review_count is not None
            and reputation_snapshot.review_count
            < rule.minimum_review_count
        ):
            return False

        if (
            rule.minimum_percentile_rank is not None
            and reputation_snapshot.percentile_rank
            < rule.minimum_percentile_rank
        ):
            return False

        if (
            rule.minimum_trust_score is not None
            and reputation_snapshot.trust_score
            < rule.minimum_trust_score
        ):
            return False

        if performance_metrics is None:
            return cls._passes_without_metrics(rule)

        if (
            rule.minimum_completed_orders is not None
            and performance_metrics.total_orders_completed
            < rule.minimum_completed_orders
        ):
            return False

        if (
            rule.maximum_lateness_rate is not None
            and performance_metrics.lateness_rate
            > rule.maximum_lateness_rate
        ):
            return False

        if (
            rule.maximum_dispute_rate is not None
            and performance_metrics.dispute_rate
            > rule.maximum_dispute_rate
        ):
            return False

        return True

    @staticmethod
    def _passes_without_metrics(
        rule: RewardRule,
    ) -> bool:
        """
        If metrics are unavailable, fail rules that depend on them.
        """

        metric_required_fields = [
            rule.minimum_completed_orders,
            rule.maximum_lateness_rate,
            rule.maximum_dispute_rate,
        ]

        return all(
            field is None
            for field in metric_required_fields
        )

    # ---------------------------------------------------------
    # QUALIFICATION FLAGS
    # ---------------------------------------------------------

    @staticmethod
    def qualifies_for_elite_status(
        *,
        reputation_snapshot: WriterReputationSnapshot,
    ) -> bool:
        """
        Marketplace elite writer.
        """

        return (
            reputation_snapshot.trust_score
            >= Decimal("90.00")
            and reputation_snapshot.percentile_rank
            >= Decimal("95.00")
            and reputation_snapshot.review_count >= 25
        )

    @staticmethod
    def qualifies_for_priority_routing(
        *,
        reputation_snapshot: WriterReputationSnapshot,
    ) -> bool:
        """
        Preferred routing pool.
        """

        return (
            reputation_snapshot.trust_score
            >= Decimal("80.00")
        )

    @staticmethod
    def qualifies_for_bonus(
        *,
        reputation_snapshot: WriterReputationSnapshot,
    ) -> bool:
        """
        Simple bonus gate.
        """

        return (
            reputation_snapshot.rating
            >= Decimal("4.80")
            and reputation_snapshot.review_count >= 10
        )