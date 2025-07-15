from decimal import Decimal, ROUND_HALF_UP


class CompositeScoreService:
    @staticmethod
    def compute_score(metrics: dict) -> Decimal:
        score = Decimal("0.00")

        rating = metrics.get("avg_rating", 0)
        revision_rate = metrics.get("revision_rate", 0)
        dispute_rate = metrics.get("dispute_rate", 0)
        lateness_rate = metrics.get("lateness_rate", 0)
        cancellation_rate = metrics.get("cancellation_rate", 0)
        preferred_rate = metrics.get("preferred_rate", 0)

        score += Decimal(rating) * Decimal("10")
        score += Decimal(preferred_rate) * Decimal("15")
        score -= Decimal(revision_rate) * Decimal("10")
        score -= Decimal(dispute_rate) * Decimal("15")
        score -= Decimal(lateness_rate) * Decimal("15")
        score -= Decimal(cancellation_rate) * Decimal("10")

        score = max(min(score, Decimal("100.00")), Decimal("0.00"))

        return score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def compute_percentile(writer_score, all_scores):
        if not all_scores:
            return 100

        below = sum(1 for s in all_scores if s < writer_score)
        percentile = (below / len(all_scores)) * 100

        return round(percentile, 2)