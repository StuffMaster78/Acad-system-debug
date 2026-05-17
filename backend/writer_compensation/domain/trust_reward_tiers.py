from decimal import Decimal


class TrustRewardTiers:

    TIERS = [
        {
            "min_score": Decimal("95"),
            "bonus": Decimal("50.00"),
            "label": "Legend Tier",
        },
        {
            "min_score": Decimal("90"),
            "bonus": Decimal("30.00"),
            "label": "Elite Tier",
        },
        {
            "min_score": Decimal("85"),
            "bonus": Decimal("20.00"),
            "label": "Gold Tier",
        },
        {
            "min_score": Decimal("80"),
            "bonus": Decimal("10.00"),
            "label": "Silver Tier",
        },
    ]

    @classmethod
    def resolve(cls, score):
        for tier in cls.TIERS:
            if score >= tier["min_score"]:
                return tier

        return None