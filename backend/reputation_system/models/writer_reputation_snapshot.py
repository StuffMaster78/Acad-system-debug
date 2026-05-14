from django.db import models
from decimal import Decimal

class WriterReputationSnapshot(models.Model):
    """
    Aggregated reputation state for writers.
    """

    writer_id = models.UUIDField(
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

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @classmethod
    def recalculate(cls, writer_id: str) -> None:
        """
        Placeholder for aggregation logic.
        """

        snapshot, _ = cls.objects.get_or_create(
            writer_id=writer_id,
        )

        # Later: plug ReviewQueryService here
        snapshot.save()