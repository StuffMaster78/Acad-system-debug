from decimal import Decimal


class TargetTypeWeights:
    """
    Defines how different target types influence reputation scoring.

    This is the single source of truth for:
        - website reviews
        - writer reviews
        - order-based reviews
        - class orders
        - special orders
    """

    WEBSITE = Decimal("1.00")
    WRITER = Decimal("1.00")

    ORDER = Decimal("0.90")
    CLASS_ORDER = Decimal("0.85")
    SPECIAL_ORDER = Decimal("0.95")

    @classmethod
    def get(cls, target_type: str) -> Decimal:
        """
        Resolve weighting for a given target type.

        Defaults to neutral weight if unknown.
        """

        mapping = {
            "website": cls.WEBSITE,
            "writer": cls.WRITER,
            "order": cls.ORDER,
            "class_order": cls.CLASS_ORDER,
            "special_order": cls.SPECIAL_ORDER,
        }

        return mapping.get(target_type, Decimal("1.00"))