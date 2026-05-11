from django.db import models


class TipIdempotencyKey(models.Model):
    """
    Ensures tip creation is safe under retries.

    Guarantees:
        - same request cannot create multiple tips
    This model protects the system against:
        - repeated API submissions
        - provider retries
        - frontend double-clicks
        - webhook duplication
    """

    sender = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="tip_idempotency_keys",
    )

    key = models.CharField(max_length=255)

    tip = models.OneToOneField(
        "tips.Tip",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    request_hash = models.CharField(
        max_length=64,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        )

    class Meta:
        unique_together = ("sender", "key")