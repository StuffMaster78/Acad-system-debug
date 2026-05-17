from decimal import Decimal


class BonusThresholds:
    """
    Canonical bonus rules used across:
        - BonusService
        - Consumers
        - Future analytics
    """

    PERFORMANCE_BONUS_RATES = {
        (Decimal("4.8"), Decimal("0.98")): Decimal("0.15"),
        (Decimal("4.5"), Decimal("0.95")): Decimal("0.10"),
        (Decimal("4.0"), Decimal("0.90")): Decimal("0.05"),
    }

    MILESTONES = [
        (10, Decimal("50.00")),
        (50, Decimal("150.00")),
        (100, Decimal("300.00")),
        (250, Decimal("750.00")),
        (500, Decimal("1500.00")),
    ]

    RETENTION_BASES = {
        "high": Decimal("25.00"),
        "mid": Decimal("15.00"),
        "low": Decimal("5.00"),
    }

    MIN_RATING = Decimal("4.0")
    MAX_RATING = Decimal("5.0")