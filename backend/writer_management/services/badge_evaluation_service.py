# writer_management.services.badge_evaluation_service.py

from writer_management.models.badges import Badge
from writer_management.services.writer_badge_award_service import (
    WriterBadgeAwardService,
)
from writer_management.services.performance_aggregator import (
    WriterPerformanceAggregator,
)


class BadgeEvaluationService:
    @staticmethod
    def evaluate(writer):
        """
        Evaluate all auto-awardable badges for a given writer.
        """
        metrics = WriterPerformanceAggregator.aggregate(writer)
        badges = Badge.objects.filter(is_active=True, auto_award=True)

        awarded = []

        for badge in badges:
            if BadgeEvaluationService._meets_rule(writer, badge, metrics):
                result = WriterBadgeAwardService.award_badge(
                    writer, badge, is_auto=True
                )
                if result:
                    awarded.append(result)

        return awarded

    @staticmethod
    def _meets_rule(writer, badge: Badge, metrics: dict) -> bool:
        """
        Evaluates badge eligibility based on badge.rule_code.
        Rule codes should map to pre-defined conditions.
        """

        if badge.rule_code == "top_10_3_weeks":
            return metrics.get("weeks_in_top_10", 0) >= 3
        elif badge.rule_code == "big_earner":
            return metrics.get("total_earned", 0) >= 1000
        elif badge.rule_code == "no_revisions":
            return metrics.get("orders_with_zero_revisions", 0) >= 10
        elif badge.rule_code == "no_disputes":
            return metrics.get("dispute_free_orders", 0) >= 20
        elif badge.rule_code == "hot_streak":
            return metrics.get("daily_activity_streak", 0) >= 7
        elif badge.rule_code == "chosen_one":
            return metrics.get("preferred_by_clients", 0) >= 5
        else:
            return False