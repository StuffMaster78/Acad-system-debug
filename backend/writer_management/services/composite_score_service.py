from decimal import Decimal
from writer_management.models.performance_snapshot import (
    WriterPerformanceSnapshot
)

class CompositeScoreService:
    @staticmethod
    def calculate(
        snapshot: WriterPerformanceSnapshot
    ) -> Decimal:
        """
        Returns a composite score from weighted performance metrics.
        Scale: 0.00 to 100.00
        """
        try:
            rating_score = snapshot.average_rating * Decimal("20")  # Max 100
            completion_score = snapshot.completion_rate * Decimal("100")
            revision_penalty = Decimal("100") - (
                snapshot.revision_rate * Decimal("100")
            )
            lateness_penalty = Decimal("100") - (
                snapshot.lateness_rate * Decimal("100")
            )
            client_pref_score = snapshot.preferred_order_rate * Decimal("100")

            composite = (
                rating_score * Decimal("0.30")
                + completion_score * Decimal("0.25")
                + revision_penalty * Decimal("0.15")
                + lateness_penalty * Decimal("0.15")
                + client_pref_score * Decimal("0.15")
            )

            return composite.quantize(Decimal("0.01"))
        except Exception:
            return Decimal("0.00")