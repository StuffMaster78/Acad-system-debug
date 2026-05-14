from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RatingSchema:
    """
    Defines rating structure rules.

    Central source of truth for rating constraints.
    """

    min_rating: Decimal = Decimal("0.00")
    max_rating: Decimal = Decimal("5.00")
    precision: int = 2

    def validate(self, value: Decimal) -> bool:
        """
        Validate rating bounds.

        Returns:
            bool: True if valid rating.
        """

        return self.min_rating <= value <= self.max_rating

    def clamp(self, value: Decimal) -> Decimal:
        """
        Clamp rating into valid range.

        Useful for defensive programming.
        """

        if value < self.min_rating:
            return self.min_rating

        if value > self.max_rating:
            return self.max_rating

        return value