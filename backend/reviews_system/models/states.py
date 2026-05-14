from django.db import models


class ReviewState(models.TextChoices):
    """Moderation states for reviews."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    FLAGGED = "flagged", "Flagged"


class ReviewVisibility(models.TextChoices):
    """Visibility states for reviews."""

    PUBLIC = "public", "Public"
    SHADOWED = "shadowed", "Shadowed"
    INTERNAL = "internal", "Internal"
    REMOVED = "removed", "Removed"
    UNDER_REVIEW = "under_review", "Under Review"