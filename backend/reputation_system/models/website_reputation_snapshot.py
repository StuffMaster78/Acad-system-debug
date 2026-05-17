from django.db import models
from decimal import Decimal

class WebsiteReputationSnapshot(models.Model):
    """
    Aggregated reputation state for websites.
    """

    website_id = models.UUIDField(
        unique=True,
        db_index=True,
    )

    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    review_count = models.PositiveIntegerField(
        default=0,
    )
    # For a richer competitive metrics
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Precomputed reputation intelligence. "
            "Used for rewards, routing, "
            "leaderboards, and analytics."
        ),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @classmethod
    def recalculate(cls, website_id: str) -> None:
        """
        Placeholder for aggregation logic.
        """

        snapshot, _ = cls.objects.get_or_create(
            website_id=website_id,
        )

        snapshot.save()