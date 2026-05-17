from enum import Enum


class VisibilityState(str, Enum):
    """
    Controls public exposure of a review.
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    HIDDEN = "hidden"