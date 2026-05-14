class ReputationRules:
    """
    Business rules for reputation scoring.
    """

    MIN_REVIEWS_FOR_TRUST = 3

    WEIGHT_WEBSITE = 0.3
    WEIGHT_WRITER = 0.7

    @staticmethod
    def is_trusted(review_count: int) -> bool:
        """
        Determine if entity is statistically trusted.
        """

        return review_count >= ReputationRules.MIN_REVIEWS_FOR_TRUST