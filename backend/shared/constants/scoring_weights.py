from decimal import Decimal


class ScoringWeights:
    """
    Legacy fallback weights (should be replaced by domain weights).
    """

    WEBSITE_WEIGHT = Decimal("1.00")
    WRITER_WEIGHT = Decimal("1.00")