class ReviewEventType:
    """
    Canonical review event names.
    """

    CREATED = "review.created"
    UPDATED = "review.updated"

    APPROVED = "review.approved"
    REJECTED = "review.rejected"

    SHADOWED = "review.shadowed"
    FLAGGED = "review.flagged"