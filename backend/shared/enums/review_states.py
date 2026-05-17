from enum import Enum


class ReviewState(str, Enum):
    """
    Lifecycle state of a review.
    """

    PENDING = "pending"
    APPROVED = "approved"
    SHADOWED = "shadowed"
    REJECTED = "rejected"
    FLAGGED = "flagged"